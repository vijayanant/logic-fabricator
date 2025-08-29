from .fabric import (
    BeliefSystem,
    Condition,
    ContradictionEngine,
    Effect,
    Rule,
    Statement,
)
from .llm_parser import LLMParser
from .ir_translator import IRTranslator
from .ir.ir_types import IRRule, IRStatement
from .exceptions import UnsupportedIRFeatureError
from typing import Union

# Global instances for handlers (will be passed to handlers)
_belief_system: BeliefSystem = None
_llm_parser: LLMParser = None
_ir_translator: IRTranslator = None

def print_welcome():
    """Prints the welcome message and help text."""
    print("\n--- Logic Fabricator Workbench ---")
    print("A REPL for exploring belief systems.")
    print_help()


def print_help():
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
    print("  forks                              (Show the number of forked realities)")
    print("  reset                              (Start with a fresh belief system)")
    print("  help                               (Show this help message)")
    print("  exit                               (Leave the workbench)")

def handle_rule_command(raw_input_text: str):
    global _belief_system
    if not raw_input_text:
        print("  !! Error: rule command requires a natural language rule.")
        return
    try:
        ir_object = _llm_parser.parse_natural_language(raw_input_text)
        if not ir_object:
            print("  !! Error: Could not parse the rule. LLM returned empty.")
            return
        
        if isinstance(ir_object, IRRule):
            new_rule = _ir_translator.translate_ir_rule(ir_object)
            _belief_system.rules.append(new_rule)
            print(f"  ++ Fabricated Rule: {new_rule}")
        else:
            print(f"  !! Error: Expected a rule, but LLM parsed a {type(ir_object).__name__}. Please provide a rule in 'if ... then ...' format.")

    except UnsupportedIRFeatureError as e:
        print(f"  !! Feature not supported: {e}")
    except Exception as e:
        print(f"  !! Error fabricating rule: {e}")

def handle_effect_command(raw_input_text: str):
    global _belief_system
    if not raw_input_text:
        print("  !! Error: effect command requires a natural language effect rule.")
        return
    try:
        ir_object = _llm_parser.parse_natural_language(raw_input_text)
        if not ir_object:
            print("  !! Error: Could not parse the effect rule. LLM returned empty.")
            return
        
        if isinstance(ir_object, IRRule) and ir_object.rule_type == "effect":
            new_rule = _ir_translator.translate_ir_rule(ir_object)
            _belief_system.rules.append(new_rule)
            print(f"  ++ Fabricated Effect Rule: {new_rule}")
        else:
            print(f"  !! Error: Expected an effect rule, but LLM parsed a {type(ir_object).__name__} or a non-effect rule. Please provide an effect rule in 'if ... then ...' format.")

    except UnsupportedIRFeatureError as e:
        print(f"  !! Feature not supported: {e}")
    except Exception as e:
        print(f"  !! Error fabricating effect rule: {e}")

def handle_sim_command(raw_input_text: str):
    global _belief_system
    if not raw_input_text:
        print("  !! Error: sim command requires a natural language statement.")
        return
    try:
        ir_object = _llm_parser.parse_natural_language(raw_input_text)
        if not ir_object:
            print("  !! Error: Could not parse the statement. LLM returned empty.")
            return
        
        if isinstance(ir_object, Statement):
            statement = ir_object # LLMParser can return Statement directly if it's a simple statement
        elif isinstance(ir_object, IRStatement):
            statement = _ir_translator.translate_ir_statement(ir_object)
        else:
            print(f"  !! Error: Expected a statement, but LLM parsed a {type(ir_object).__name__}. Please provide a simple statement.")
            return

        print(
            f"\n... Simulating: {'NOT ' if statement.negated else ''}{statement.verb} {' '.join(statement.terms)}"
        )

        state_before = _belief_system.world_state.copy()
        sim_result = _belief_system.simulate([statement])
        state_after = _belief_system.world_state

        print("\n--- Simulation Report ---")
        if sim_result.forked_belief_system:
            print("  !! CONTRADICTION DETECTED: Reality has forked.")
            _belief_system = sim_result.forked_belief_system
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

def handle_state_command():
    print("--- World State ---")
    if not _belief_system.world_state:
        print("(empty)")
    else:
        for k, v in _belief_system.world_state.items():
            print(f"  {k}: {v}")

def handle_rules_command():
    print("--- Active Rules ---")
    if not _belief_system.rules:
        print("(none)")
    else:
        for i, rule in enumerate(_belief_system.rules):
            print(
                f"  {i + 1}: {rule}" 
            )  # Relies on a __str__ or __repr__ for Rule

def handle_statements_command():
    print("--- Current Facts ---")
    if not _belief_system.statements:
        print("(none)")
    else:
        for stmt in sorted(
            list(_belief_system.statements), key=lambda s: s.verb
        ):
            print(
                f"  - {'NOT ' if stmt.negated else ''}{stmt.verb} {' '.join(stmt.terms)}"
            )

def handle_forks_command():
    print(f"--- Forks ---")
    print(f"This reality has forked {len(_belief_system.forks)} time(s).")

def handle_reset_command():
    global _belief_system, _llm_parser, _ir_translator
    print("Purging reality. A new belief system is born.")
    _belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    _llm_parser = LLMParser()
    _ir_translator = IRTranslator()
    return _belief_system # Return the new belief system for main to update

def handle_exit_command():
    print("Exiting workbench.")
    exit()

def main():
    global _belief_system, _llm_parser, _ir_translator
    _belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
    _llm_parser = LLMParser()
    _ir_translator = IRTranslator()

    command_handlers = {
        "rule": handle_rule_command,
        "effect": handle_effect_command,
        "sim": handle_sim_command,
        "state": handle_state_command,
        "rules": handle_rules_command,
        "statements": handle_statements_command,
        "forks": handle_forks_command,
        "reset": handle_reset_command,
        "help": print_help,
        "exit": handle_exit_command,
        "quit": handle_exit_command,
    }

    print_welcome()

    while True:
        try:
            user_input = input("\n>> ").strip()
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1) # Split only on first space to get command and rest of input
            command = parts[0].lower()
            raw_input_text = parts[1] if len(parts) > 1 else ""

            if command in command_handlers:
                if command in ["reset", "exit", "quit"]:
                    # These commands handle their own global state or exit
                    command_handlers[command]()
                elif command in ["state", "rules", "statements", "forks", "help"]:
                    # These commands don't take raw_input_text
                    command_handlers[command]()
                else:
                    # Commands that take raw_input_text
                    command_handlers[command](raw_input_text)
            else:
                print(f"  !! Unknown command: '{command}'. Type 'help' for a list of commands.")

        except KeyboardInterrupt:
            print("\nExiting workbench.")
            break
        except Exception as e:
            print(f"\n  !! A critical error occurred: {e}")
            print("  !! The fabric of reality may be unstable.")


if __name__ == "__main__":
    main()

