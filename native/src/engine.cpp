#include "spence/engine.h"
#include "spence/player.h"
#include <algorithm>

namespace spence {

WorkerThread::WorkerThread() = default;

WorkerThread::~WorkerThread() {
    stop();
}

void WorkerThread::start() {
    running_ = true;
    thread_ = std::thread(&WorkerThread::run, this);
}

void WorkerThread::stop() {
    if (running_) {
        running_ = false;
        cv_.notify_one();
        if (thread_.joinable()) {
            thread_.join();
        }
    }
}

void WorkerThread::submit(Task&& task) {
    {
        std::lock_guard lock(mutex_);
        tasks_.push_back(std::move(task));
    }
    cv_.notify_one();
}

bool WorkerThread::try_steal(Task& task) {
    std::lock_guard lock(mutex_);
    if (tasks_.empty()) {
        return false;
    }
    task = std::move(tasks_.front());
    tasks_.pop_front();
    return true;
}

void WorkerThread::run() {
    while (running_) {
        Task task;
        
        {
            std::unique_lock lock(mutex_);
            cv_.wait(lock, [this] { return !tasks_.empty() || !running_; });
            
            if (!running_) break;
            
            if (!tasks_.empty()) {
                task = std::move(tasks_.front());
                tasks_.pop_front();
            }
        }
        
        if (task.execute) {
            task.execute();
        }
    }
}

ThreadPool::ThreadPool(uint32_t size) {
    workers_.reserve(size);
    for (uint32_t i = 0; i < size; ++i) {
        auto worker = std::make_unique<WorkerThread>();
        worker->start();
        workers_.push_back(std::move(worker));
    }
}

ThreadPool::~ThreadPool() {
    shutdown();
}

void ThreadPool::submit(Task&& task) {
    if (workers_.empty()) return;
    
    // Round-robin with work stealing fallback
    uint32_t idx = next_worker_.fetch_add(1, std::memory_order_relaxed) % workers_.size();
    workers_[idx]->submit(std::move(task));
}

void ThreadPool::shutdown() {
    for (auto& worker : workers_) {
        worker->stop();
    }
    workers_.clear();
}

Engine::Engine(uint32_t thread_pool_size)
    : thread_pool_(std::make_unique<ThreadPool>(thread_pool_size)) {
}

Engine::~Engine() = default;

std::shared_ptr<Player> Engine::create_player() {
    uint64_t id = allocate_player_id();
    auto player = std::make_shared<Player>(this, id);
    
    std::lock_guard lock(players_mutex_);
    players_.push_back(player);
    
    return player;
}

void Engine::destroy_player(uint64_t player_id) {
    std::lock_guard lock(players_mutex_);
    players_.erase(
        std::remove_if(players_.begin(), players_.end(),
            [player_id](const std::weak_ptr<Player>& wp) {
                auto sp = wp.lock();
                return !sp || sp->id() == player_id;
            }),
        players_.end()
    );
}

void Engine::submit_task(Task&& task) {
    thread_pool_->submit(std::move(task));
}

uint64_t Engine::allocate_player_id() {
    return next_player_id_.fetch_add(1, std::memory_order_relaxed);
}

}
