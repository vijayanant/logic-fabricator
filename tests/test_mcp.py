
import pytest
from logic_fabricator.mcp import MCP
from logic_fabricator.fabric import ForkingStrategy
from .mocks import MockDriver


def test_mcp_can_use_mock_database():
    """
    This test fails because the MCP is hard-coded to use the real Neo4j driver.
    We want to refactor it to accept a driver in its constructor.
    """
    mock_driver = MockDriver()
    mcp = MCP(driver=mock_driver)
    
    belief_system_id = mcp.create_belief_system("Test Belief System", ForkingStrategy.COEXIST)
    
    assert belief_system_id is not None
    assert belief_system_id in mcp.belief_systems
