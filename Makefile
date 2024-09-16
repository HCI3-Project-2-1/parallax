BUILD_DIR = build

CXX = clang++

CMAKE_COMMAND = cmake

CMAKE_FLAGS = -DCMAKE_C_COMPILER=$(CC) -DCMAKE_CXX_COMPILER=$(CXX)

all: $(BUILD_DIR)/Makefile
	$(MAKE) -C $(BUILD_DIR)

$(BUILD_DIR)/Makefile:
	mkdir -p $(BUILD_DIR)
	cd $(BUILD_DIR) && $(CMAKE_COMMAND) $(CMAKE_FLAGS) ..

clean:
	$(MAKE) -C $(BUILD_DIR) clean
	rm -rf $(BUILD_DIR)
