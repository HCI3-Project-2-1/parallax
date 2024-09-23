- Use `std::queue` for shared data (eye-tracking position) between threads.
- Create a **producer-consumer model**:
  - **Vision thread (producer)**: Pushes eye position data into the queue.
  - **Engine thread (consumer)**: Reads the latest data from the queue and applies it for camera movement.
  
- Use a **mutex** to safely access the shared queue between threads.
- Ensure the engine pulls data only once per frame render:
  - Engine thread checks for the most recent eye position data after each render.
  - Clear the queue after reading the data to avoid processing old data.

- Spawn the **vision thread** in your engine startup function (e.g., `_ready()`).
- Ensure proper thread cleanup on shutdown to avoid dangling threads or memory leaks.

- Test for latency: Ensure camera movement is responsive to real-time eye position updates.
- If necessary, implement **async queue** to allow non-blocking data transmission and avoid frame drops.

- Optimize thread synchronization if frame drops or jitter occur during data transmission.
