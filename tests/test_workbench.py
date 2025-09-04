import io
from contextlib import redirect_stdout

# Import the functions and global state we need to manipulate
from logic_fabricator.workbench import (
    handle_reset_command,
    handle_sim_command,
    handle_history_command, # This import will fail
)

def test_history_command_prints_mcp_records():
    """
    Tests that the 'history' command function prints MCP records from the belief system.
    """
    # Initialize the global belief system used by the handlers
    handle_reset_command()

    # Run a simulation to create a history record
    handle_sim_command("socrates is a man")

    output_capture = io.StringIO()
    with redirect_stdout(output_capture):
        handle_history_command()

    output = output_capture.getvalue()

    # Assert that the output contains the string representation of the SimulationRecord
    assert "--- History ---" in output
    assert "SimulationRecord" in output
    assert "initial_statements=[Statement(is ['Socrates', 'a_man'], neg=False, prio=1.0)]" in output