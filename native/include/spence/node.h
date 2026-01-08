#pragma once

#include <memory>
#include <string>

namespace spence {

class Engine;
class Player;

struct NodeConfig {
    uint32_t thread_pool_size = 4;
};

class Node {
public:
    explicit Node(const NodeConfig& config = NodeConfig{});
    ~Node();
    
    std::shared_ptr<Player> create_player();
    
    Engine* engine() { return engine_.get(); }
    
private:
    std::unique_ptr<Engine> engine_;
};

}
