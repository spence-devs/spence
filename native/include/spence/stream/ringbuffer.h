#pragma once

#include <vector>
#include <mutex>
#include <condition_variable>
#include <optional>

namespace spence {

template <typename T>
class RingBuffer {
public:
    explicit RingBuffer(size_t capacity)
        : buffer_(capacity), capacity_(capacity) {}
    
    bool try_push(const T& item) {
        std::unique_lock lock(mutex_);
        if (size_ >= capacity_) {
            return false;
        }
        
        buffer_[write_pos_] = item;
        write_pos_ = (write_pos_ + 1) % capacity_;
        size_++;
        
        cv_read_.notify_one();
        return true;
    }
    
    bool try_push(T&& item) {
        std::unique_lock lock(mutex_);
        if (size_ >= capacity_) {
            return false;
        }
        
        buffer_[write_pos_] = std::move(item);
        write_pos_ = (write_pos_ + 1) % capacity_;
        size_++;
        
        cv_read_.notify_one();
        return true;
    }
    
    std::optional<T> try_pop() {
        std::unique_lock lock(mutex_);
        if (size_ == 0) {
            return std::nullopt;
        }
        
        T item = std::move(buffer_[read_pos_]);
        read_pos_ = (read_pos_ + 1) % capacity_;
        size_--;
        
        cv_write_.notify_one();
        return item;
    }
    
    T pop_or_wait() {
        std::unique_lock lock(mutex_);
        cv_read_.wait(lock, [this] { return size_ > 0; });
        
        T item = std::move(buffer_[read_pos_]);
        read_pos_ = (read_pos_ + 1) % capacity_;
        size_--;
        
        cv_write_.notify_one();
        return item;
    }
    
    size_t size() const {
        std::unique_lock lock(mutex_);
        return size_;
    }
    
    bool empty() const {
        return size() == 0;
    }
    
    bool full() const {
        std::unique_lock lock(mutex_);
        return size_ >= capacity_;
    }
    
    void clear() {
        std::unique_lock lock(mutex_);
        read_pos_ = 0;
        write_pos_ = 0;
        size_ = 0;
        cv_write_.notify_all();
    }
    
private:
    std::vector<T> buffer_;
    size_t capacity_;
    size_t read_pos_ = 0;
    size_t write_pos_ = 0;
    size_t size_ = 0;
    
    mutable std::mutex mutex_;
    std::condition_variable cv_read_;
    std::condition_variable cv_write_;
};

}
