#pragma once

#include <cstdint>
#include <memory>
#include <vector>
#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>
#include <functional>

namespace spence {

class Player;

struct Task {
    uint64_t player_id;
    uint64_t frame_index;
    std::function<void()> execute;
};

class WorkerThread {
public:
    WorkerThread();
    ~WorkerThread();
    
    void start();
    void stop();
    void submit(Task&& task);
    bool try_steal(Task& task);
    
private:
    void run();
    
    std::deque<Task> tasks_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::thread thread_;
    std::atomic<bool> running_{false};
};

class ThreadPool {
public:
    explicit ThreadPool(uint32_t size);
    ~ThreadPool();
    
    void submit(Task&& task);
    void shutdown();
    
private:
    std::vector<std::unique_ptr<WorkerThread>> workers_;
    std::atomic<uint32_t> next_worker_{0};
};

class Engine {
public:
    explicit Engine(uint32_t thread_pool_size = 4);
    ~Engine();
    
    std::shared_ptr<Player> create_player();
    void destroy_player(uint64_t player_id);
    
    void submit_task(Task&& task);
    
    uint64_t allocate_player_id();
    
private:
    std::unique_ptr<ThreadPool> thread_pool_;
    std::atomic<uint64_t> next_player_id_{1};
    
    std::mutex players_mutex_;
    std::vector<std::weak_ptr<Player>> players_;
};

}
