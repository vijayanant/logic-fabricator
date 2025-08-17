import sys
sys.path.insert(0, 'src')

from logic_fabricator.fabric import (
    BeliefSystem,
    Condition,
    ContradictionEngine,
    Effect,
    Rule,
    Statement,
)

def parse_statement(parts, negated_word="not"):
    """Parses a list of strings into a Statement object."""
    negated = False
    if parts and parts[-1].lower() == negated_word:
        negated = True
        parts.pop()
    if not parts:
        return None, "Error: Statement needs at least a verb."
    verb = parts[0]
    terms = parts[1:]
    return Statement(verb=verb, terms=terms, negated=negated), None

def print_welcome():
    """Prints the welcome message and help text."""
    print("\n--- Logic Fabricator Workbench ---")
    print("A REPL for exploring belief systems.")
    print_help()

def print_help():
    """Prints the command help."""
    print("\nCommands:")
    print("  rule <condition> -> <consequence>  (e.g., rule is ?x a_man -> is ?x mortal)")
    print("  effect <condition> -> <op> <key> <value> (e.g., effect is ?x mortal -> increment population 1)")
    print("  sim <statement>                    (e.g., sim is socrates a_man)")
    print("  state                              (Show the current world_state)")
    print("  rules                              (List all active rules)")
    print("  statements                         (List all current facts)")
    print("  forks                              (Show the number of forked realities)")
    print("  reset                              (Start with a fresh belief system)")
    print("  help                               (Show this help message)")
    print("  exit                               (Leave the workbench)")


def main():
    """The main entry point for the interactive logic playground."""
    belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())

    print_welcome()

    while True:
        try:
            user_input = input("\n>> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()

            if command in ["exit", "quit"]:
                print("Exiting workbench.")
                break
            elif command == "help":
                print_help()
            elif command == "reset":
                print("Purging reality. A new belief system is born.")
                belief_system = BeliefSystem(rules=[], contradiction_engine=ContradictionEngine())
            elif command == "state":
                print("--- World State ---")
                if not belief_system.world_state:
                    print("(empty)")
                else:
                    for k, v in belief_system.world_state.items():
                        print(f"  {k}: {v}")
            elif command == "rules":
                print("--- Active Rules ---")
                if not belief_system.rules:
                    print("(none)")
                else:
                    for i, rule in enumerate(belief_system.rules):
                        print(f"  {i+1}: {rule}") # Relies on a __str__ or __repr__ for Rule
            elif command == "statements":
                print("--- Current Facts ---")
                if not belief_system.statements:
                    print("(none)")
                else:
                    for stmt in sorted(list(belief_system.statements), key=lambda s: s.verb):
                         print(f"  - {'NOT ' if stmt.negated else ''}{stmt.verb} {' '.join(stmt.terms)}")
            elif command == "forks":
                print(f"--- Forks ---")
                print(f"This reality has forked {len(belief_system.forks)} time(s).")

            elif command == "rule":
                try:
                    arrow_index = parts.index("->")
                    condition_parts = parts[1:arrow_index]
                    consequence_parts = parts[arrow_index + 1:]

                    cond_verb = condition_parts[0]
                    cond_terms = condition_parts[1:]
                    condition = Condition(verb=cond_verb, terms=cond_terms)

                    consequence, err = parse_statement(consequence_parts)
                    if err:
                        print(f"  !! Error in consequence: {err}")
                        continue
                    
                    new_rule = Rule(condition=condition, consequences=[consequence])
                    belief_system.rules.append(new_rule)
                    print(f"  ++ Fabricated Rule: {new_rule}")
                except (ValueError, IndexError):
                    print("  !! Invalid rule syntax. Use: rule <condition> -> <consequence>")

            elif command == "effect":
                try:
                    arrow_index = parts.index("->")
                    condition_parts = parts[1:arrow_index]
                    effect_parts = parts[arrow_index + 1:]

                    cond_verb = condition_parts[0]
                    cond_terms = condition_parts[1:]
                    condition = Condition(verb=cond_verb, terms=cond_terms)
                    
                    op, key, value_str = effect_parts
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = value_str

                    effect = Effect(target="world_state", attribute=key, operation=op, value=value)
                    new_rule = Rule(condition=condition, consequences=[effect])
                    belief_system.rules.append(new_rule)
                    print(f"  ++ Fabricated Effect Rule: {new_rule}")
                except (ValueError, IndexError):
                    print("  !! Invalid effect syntax. Use: effect <condition> -> <op> <key> <value>")

            elif command == "sim":
                statement_parts = parts[1:]
                statement, err = parse_statement(statement_parts)
                if err:
                    print(f"  !! {err}")
                    continue

                print(f"\n... Simulating: {'NOT ' if statement.negated else ''}{statement.verb} {' '.join(statement.terms)}")
                
                state_before = belief_system.world_state.copy()
                sim_result = belief_system.simulate([statement])
                state_after = belief_system.world_state

                print("\n--- Simulation Report ---")
                if sim_result.forked_belief_system:
                    print("  !! CONTRADICTION DETECTED: Reality has forked.")
                    belief_system = sim_result.forked_belief_system
                    print("  >> Switched context to the new forked reality.")
                
                if sim_result.derived_facts:
                    print("  >> Derived Facts:")
                    for fact in sim_result.derived_facts:
                        print(f"     - {'NOT ' if fact.negated else ''}{fact.verb} {' '.join(fact.terms)}")
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