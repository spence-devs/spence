#include "spence/node.h"
#include "spence/engine.h"
#include "spence/player.h"

namespace spence {

Node::Node(const NodeConfig& config)
    : engine_(std::make_unique<Engine>(config.thread_pool_size)) {
}

Node::~Node() = default;

std::shared_ptr<Player> Node::create_player() {
    return engine_->create_player();
}

}
