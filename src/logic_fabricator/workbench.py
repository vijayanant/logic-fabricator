import structlog
from .config import configure_logging  # Import the logging configuration function
from .core_types import BeliefSystem, ContradictionEngine, Statement
from .llm_parser import LLMParser
from .ir_translator import IRTranslator
from .ir.ir_types import IRRule, IRStatement
from .exceptions import UnsupportedIRFeatureError
from typing import Union
from .mcp import MCP
from .neo4j_adapter import Neo4jAdapter

# Get a structlog logger instance for this module
logger = structlog.get_logger(__name__)


class Workbench:
    def __init__(self):
        self.belief_system: BeliefSystem = BeliefSystem(
            rules=[], contradiction_engine=ContradictionEngine()
        )
        self.llm_parser: LLMParser = LLMParser()
        self.ir_translator: IRTranslator = IRTranslator()
        self.mcp: MCP = MCP(db_adapter=Neo4jAdapter())
        self.belief_system_id: str = self.mcp.create_belief_system(
            "Workbench Belief System", self.belief_system.strategy
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mcp.close()

    def print_welcome(self):
        """Prints the welcome message and help text."""
        print("\n--- Logic Fabricator Workbench ---")
        print("A REPL for exploring belief systems.")
        self.print_help()

    def print_help(self):
        """Prints the command help."""
        print("\nCommands:")
        print(
            "  rule <natural language rule>  (e.g., rule If ?x is a man, then ?x is mortal)"
        )
        print(
            "  effect <natural language effect rule> (e.g., effect If ?x is mortal, then increment population by 1)"
        )
        print("  sim <natural language statement>    (e.g., sim Alice trusts Bob.)")
        print("  state                              (Show the current world_state)")
        print("  rules                              (List all active rules)")
        print("  statements                         (List all current facts)")
        print(
            "  forks                              (Show the number of forked realities)"
        )
        print("  history                            (Show the simulation history)")
        print("  reset                              (Start with a fresh belief system)")
        print("  help                               (Show this help message)")
        print("  exit                               (Leave the workbench)")

    def handle_rule_command(self, raw_input_text: str):
        if not raw_input_text:
            print("  !! Error: rule command requires a natural language rule.")
            return
        try:
            ir_object = self.llm_parser.parse_natural_language(raw_input_text)
            if not ir_object:
                print("  !! Error: Could not parse the rule. LLM returned empty.")
                return

            if isinstance(ir_object, IRRule):
                new_rule = self.ir_translator.translate_ir_rule(ir_object)
                self.belief_system.rules.append(new_rule)
                print(f"  ++ Fabricated Rule: {new_rule}")
            else:
                print(
                    f"  !! Error: Expected a rule, but LLM parsed a {type(ir_object).__name__}. Please provide a rule in 'if ... then ...' format."
                )

        except UnsupportedIRFeatureError as e:
            print(f"  !! Feature not supported: {e}")
        except Exception as e:
            print(f"  !! Error fabricating rule: {e}")

    def handle_effect_command(self, raw_input_text: str):
        if not raw_input_text:
            print("  !! Error: effect command requires a natural language effect rule.")
            return
        try:
            ir_object = self.llm_parser.parse_natural_language(raw_input_text)
            if not ir_object:
                print(
                    "  !! Error: Could not parse the effect rule. LLM returned empty."
                )
                return

            if isinstance(ir_object, IRRule) and ir_object.rule_type == "effect":
                new_rule = self.ir_translator.translate_ir_rule(ir_object)
                self.belief_system.rules.append(new_rule)
                print(f"  ++ Fabricated Effect Rule: {new_rule}")
            else:
                print(
                    f"  !! Error: Expected an effect rule, but LLM parsed a {type(ir_object).__name__} or a non-effect rule. Please provide an effect rule in 'if ... then ...' format."
                )

        except UnsupportedIRFeatureError as e:
            print(f"  !! Feature not supported: {e}")
        except Exception as e:
            print(f"  !! Error fabricating effect rule: {e}")

    def handle_sim_command(self, raw_input_text: str):
        if not raw_input_text:
            print("  !! Error: sim command requires a natural language statement.")
            return
        try:
            ir_object = self.llm_parser.parse_natural_language(raw_input_text)
            if not ir_object:
                print("  !! Error: Could not parse the statement. LLM returned empty.")
                return

            if isinstance(ir_object, Statement):
                statement = ir_object  # LLMParser can return Statement directly if it's a simple statement
            elif isinstance(ir_object, IRStatement):
                statement = self.ir_translator.translate_ir_statement(ir_object)
            else:
                print(
                    f"  !! Error: Expected a statement, but LLM parsed a {type(ir_object).__name__}. Please provide a simple statement."
                )
                return

            print(
                f"\n... Simulating: {'NOT ' if statement.negated else ''}{statement.verb} {' '.join(statement.terms)}"
            )

            state_before = self.belief_system.world_state.copy()
            sim_result = self.belief_system.simulate([statement])
            state_after = self.belief_system.world_state

            # Persist the simulation record to the MCP
            self.mcp.simulate(self.belief_system_id, [statement])

            print("\n--- Simulation Report ---")
            if sim_result.forked_belief_system:
                print("  !! CONTRADICTION DETECTED: Reality has forked.")
                self.belief_system = sim_result.forked_belief_system
                print("  >> Switched context to the new forked reality.")

            if sim_result.derived_facts:
                print("  >> Derived Facts:")
                for fact in sim_result.derived_facts:
                    print(
                        f"     - {'NOT ' if fact.negated else ''}{fact.verb} {' '.join(fact.terms)}"
                    )
            else:
                print("  >> No new facts were derived.")

            state_changes = {
                k: (state_before.get(k), state_after.get(k))
                for k in set(state_before.keys()) | set(state_after.keys())
                if state_before.get(k) != state_after.get(k)
            }

            if state_changes:
                print("  >> World State Changes:")
                for key, (old, new) in state_changes.items():
                    print(f"     - {key}: {old or 'None'} -> {new}")
            else:
                print("  >> World state is unchanged.")

        except UnsupportedIRFeatureError as e:
            print(f"  !! Feature not supported: {e}")
        except Exception as e:
            print(f"  !! Error simulating: {e}")

    def handle_state_command(self):
        print("--- World State ---")
        if not self.belief_system.world_state:
            print("(empty)")
        else:
            for k, v in self.belief_system.world_state.items():
                print(f"  {k}: {v}")

    def handle_rules_command(self):
        print("--- Active Rules ---")
        if not self.belief_system.rules:
            print("(none)")
        else:
            for i, rule in enumerate(self.belief_system.rules):
                print(f"  {i + 1}: {rule}")  # Relies on a __str__ or __repr__ for Rule

    def handle_statements_command(self):
        print("--- Current Facts ---")
        if not self.belief_system.statements:
            print("(none)")
        else:
            for stmt in sorted(
                list(self.belief_system.statements), key=lambda s: s.verb
            ):
                print(
                    f"  - {'NOT ' if stmt.negated else ''}{stmt.verb} {' '.join(stmt.terms)}"
                )

    def handle_forks_command(self):
        print("--- Forks ---")
        print(f"This reality has forked {len(self.belief_system.forks)} time(s).")

    def handle_history_command(self):
        print("--- History ---")
        # Assuming _mcp is initialized and _belief_system_id is the current belief system ID
        history = self.mcp.get_simulation_history(self.belief_system_id)
        if not history:
            print("(empty)")
        else:
            for i, record in enumerate(history):
                print(f"  {i + 1}: {repr(record)}")

    def handle_reset_command(self):
        print("Purging reality. A new belief system is born.")
        self.belief_system = BeliefSystem(
            rules=[], contradiction_engine=ContradictionEngine()
        )
        self.llm_parser = LLMParser()
        self.ir_translator = IRTranslator()
        self.mcp: MCP = MCP(db_adapter=Neo4jAdapter())
        self.belief_system_id = self.mcp.create_belief_system(
            "Workbench Belief System", self.belief_system.strategy
        )

    def handle_exit_command(self):
        print("Exiting workbench.")
        exit()


    def run_repl(self):
        self.print_welcome()

        while True:
            try:
                user_input = input("\n>> ").strip()
                if not user_input:
                    continue

                parts = user_input.split(
                    maxsplit=1
                )  # Split only on first space to get command and rest of input
                command = parts[0].lower()
                raw_input_text = parts[1] if len(parts) > 1 else ""

                if command in self.command_handlers:
                    if command in ["reset", "exit", "quit"]:
                        # These commands handle their own global state or exit
                        self.command_handlers[command]()
                    elif command in [
                        "state",
                        "rules",
                        "statements",
                        "forks",
                        "help",
                        "history",
                    ]:
                        # These commands don't take raw_input_text
                        self.command_handlers[command]()
                    else:
                        # Commands that take raw_input_text
                        self.command_handlers[command](raw_input_text)
                else:
                    print(
                        f"  !! Unknown command: '{command}'. Type 'help' for a list of commands."
                    )

            except KeyboardInterrupt:
                print("\nExiting workbench.")
                break
            except Exception as e:
                logger.error(
                    "A critical error occurred in workbench", exc_info=True
                )  # Log the exception
                print(f"\n  !! A critical error occurred: {e}")
                print("  !! The fabric of reality may be unstable.")



def main():
    configure_logging()  # Configure structlog at the start of main
    logger.info(
        "Workbench starting up.", initial_message="Welcome to Logic Fabricator!"
    )  # Example log message

    with Workbench() as workbench:
        workbench.command_handlers = {
            "rule": workbench.handle_rule_command,
            "effect": workbench.handle_effect_command,
            "sim": workbench.handle_sim_command,
            "state": workbench.handle_state_command,
            "rules": workbench.handle_rules_command,
            "statements": workbench.handle_statements_command,
            "forks": workbench.handle_forks_command,
            "history": workbench.handle_history_command,
            "reset": workbench.handle_reset_command,
            "help": workbench.print_help,
            "exit": workbench.handle_exit_command,
            "quit": workbench.handle_exit_command,
        }

        workbench.run_repl()


if __name__ == "__main__":
    main()