import pytest
from logic_fabricator.mcp import MCP
from logic_fabricator.fabric import ForkingStrategy, Rule, Condition, Statement
from .mocks import MockAdapter

@pytest.fixture
def mcp_with_mock_adapter():
    return MCP(db_adapter=MockAdapter())

def test_mcp_create_belief_system(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    belief_system_id = mcp.create_belief_system("Test Belief System", ForkingStrategy.COEXIST)
    assert belief_system_id is not None
    assert belief_system_id in mcp.belief_systems
    assert mcp.db_adapter.belief_systems[belief_system_id]["name"] == "Test Belief System"

def test_mcp_add_rule(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    belief_system_id = mcp.create_belief_system("Test Belief System", ForkingStrategy.COEXIST)
    rule = Rule(condition=Condition(verb="is", terms=["?x", "a man"]), consequences=[Statement(verb="is", terms=["?x", "mortal"])])
    mcp.add_rule(belief_system_id, rule)
    assert rule in mcp.belief_systems[belief_system_id].rules
    assert rule in mcp.db_adapter.belief_systems[belief_system_id]["rules"]

def test_mcp_fork_belief_system(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    parent_id = mcp.create_belief_system("Parent", ForkingStrategy.COEXIST)
    fork_id = mcp.fork_belief_system(parent_id, "Fork")
    assert fork_id in mcp.belief_systems
    assert fork_id in mcp.db_adapter.belief_systems
    assert mcp.db_adapter.belief_systems[fork_id]["name"] == "Fork"

def test_mcp_simulate_persists_simulation(mcp_with_mock_adapter: MCP):
    mcp = mcp_with_mock_adapter
    belief_system_id = mcp.create_belief_system("Test", ForkingStrategy.COEXIST)
    rule = Rule(condition=Condition(verb="is", terms=["?x", "a man"]), consequences=[Statement(verb="is", terms=["?x", "mortal"])])
    mcp.add_rule(belief_system_id, rule)
    statements = [Statement(verb="is", terms=["Socrates", "a man"])]
    mcp.simulate(belief_system_id, statements)
    assert len(mcp.db_adapter.simulations) == 1
    assert mcp.db_adapter.simulations[0].initial_statements == statements