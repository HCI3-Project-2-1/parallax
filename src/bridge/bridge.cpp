#include <condition_variable>
#include <mutex>
#include <optional>
#include <queue>

template <typename T> class ThreadSafeQueue {
public:
  void push(T value) {
    std::lock_guard<std::mutex> lock(mutex_);
    queue_.push(std::move(value));
    conditionVariable_.notify_one();
  }

  std::optional<T> pop() {
    std::unique_lock<std::mutex> lock(mutex_);
    conditionVariable_.wait(lock, [this] { return !queue_.empty(); });
    if (queue_.empty()) {
      return std::nullopt;
    }
    T value = std::move(queue_.front());
    queue_.pop();
    return value;
  }

  bool empty() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return queue_.empty();
  }

  // _ suffix denotes private members
private:
  mutable std::mutex mutex_;
  std::queue<T> queue_;
  std::condition_variable conditionVariable_;
};
