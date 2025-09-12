import structlog
from typing import Optional

from .rule import Rule
from .statement import Statement
from .effect import Effect
from .contradiction import ContradictionRecord, InferredContradiction
from .forking_strategy import ForkingStrategy
from .operators import op_set, op_increment, op_decrement, op_append
from .simulation import SimulationResult, SimulationRecord

logger = structlog.get_logger(__name__)


class ContradictionEngine:
    _HYPOTHETICAL_ENTITY_ = "_HYPOTHETICAL_ENTITY_"
    def detect(self, s1: Statement, s2: Statement) -> bool:
        logger.debug(
            "Detecting contradiction between statements", statement1=s1, statement2=s2
        )
        if s1.verb == s2.verb and s1.terms == s2.terms and s1.negated != s2.negated:
            logger.info("Contradiction detected", statement1=s1, statement2=s2)
            return True

        logger.debug(
            "No contradiction detected between statements", statement1=s1, statement2=s2
        )
        return False

    def _check_one_way_conflict(
        self, rule_a: Rule, rule_b: Rule, context_rules: list[Rule]
    ) -> bool:
        logger.debug("Checking one-way conflict", rule_a=rule_a, rule_b=rule_b)
        """Checks if rule_b's condition can lead to a state that conflicts with rule_a."""
        # Use a hypothetical entity for the simulation
        hypothetical_entity = self._HYPOTHETICAL_ENTITY_

        # Create a hypothetical statement from rule_b's condition
        if not rule_b.condition.terms or not rule_b.condition.terms[0].startswith("?"):
            logger.debug("Cannot create hypothetical case for rule_b", rule_b=rule_b)
            return False  # Cannot create a hypothetical case without a variable subject

        var_name = rule_b.condition.terms[0]
        hypothetical_terms = [
            term if term != var_name else hypothetical_entity
            for term in rule_b.condition.terms
        ]
        hypothetical_statement = Statement(
            verb=rule_b.condition.verb, terms=hypothetical_terms
        )
        logger.debug("Created hypothetical statement", statement=hypothetical_statement)

        # Run the pure inference chain to see what can be derived from the hypothetical statement.
        derived_facts, _ = BeliefSystem._run_inference_chain(
            {hypothetical_statement}, context_rules
        )
        logger.debug(
            "Derived facts from hypothetical statement", derived_facts=derived_facts
        )

        # Combine initial and derived facts for checking rule applicability
        all_facts = derived_facts + [hypothetical_statement]
        logger.debug("All facts for conflict check", all_facts=all_facts)

        # Check if both rules apply to the resulting state
        bindings_a = rule_a.applies_to(all_facts)
        bindings_b = rule_b.applies_to(all_facts)
        logger.debug(
            "Rule applicability check results",
            rule_a_applies=bool(bindings_a),
            rule_b_applies=bool(bindings_b),
        )

        if bindings_a and bindings_b:
            logger.debug(
                "Both rules apply, checking consequences for contradictions",
                rule_a=rule_a,
                rule_b=rule_b,
            )
            # If both apply, check their consequences for contradictions
            for con_a in rule_a.consequences:
                if not isinstance(con_a, Statement):
                    logger.debug(
                        "Consequence A is not a Statement, skipping", consequence=con_a
                    )
                    continue
                resolved_a = Rule._resolve_statement_from_template(con_a, bindings_a)
                for con_b in rule_b.consequences:
                    if not isinstance(con_b, Statement):
                        logger.debug(
                            "Consequence B is not a Statement, skipping",
                            consequence=con_b,
                        )
                        continue
                    resolved_b = Rule._resolve_statement_from_template(
                        con_b, bindings_b
                    )
                    logger.debug(
                        "Checking for contradiction between resolved consequences",
                        resolved_a=resolved_a,
                        resolved_b=resolved_b,
                    )
                    if self.detect(resolved_a, resolved_b):
                        logger.info(
                            "One-way conflict detected between rules",
                            rule_a=rule_a,
                            rule_b=rule_b,
                            conflicting_statements=[resolved_a, resolved_b],
                        )
                        return True
        logger.debug(
            "No one-way conflict detected for this path", rule_a=rule_a, rule_b=rule_b
        )
        return False

    def detect_rule_conflict(
        self, rule_a: Rule, rule_b: Rule, context_rules: list[Rule]
    ) -> bool:
        logger.debug("Detecting rule conflict", rule_a=rule_a, rule_b=rule_b)
        """Detects if two rules could conflict, given a set of context rules."""
        # A conflict exists if rule_a can lead to a contradiction with rule_b, or vice-versa.
        conflict_found = self._check_one_way_conflict(
            rule_a, rule_b, context_rules
        ) or self._check_one_way_conflict(rule_b, rule_a, context_rules)
        if conflict_found:
            logger.info("Rule conflict detected", rule_a=rule_a, rule_b=rule_b)
        else:
            logger.debug("No rule conflict detected", rule_a=rule_a, rule_b=rule_b)
        return conflict_found


class BeliefSystem:
    _id_counter = 0  # Class-level counter for unique IDs

    def __init__(
        self,
        rules: list[Rule],
        contradiction_engine: ContradictionEngine,
        strategy: ForkingStrategy = ForkingStrategy.COEXIST,
    ):
        BeliefSystem._id_counter += 1
        self.id = BeliefSystem._id_counter
        logger.info(
            "Initializing BeliefSystem",
            belief_system_id=self.id,
            strategy=strategy,
            initial_rules_count=len(rules),
        )
        self.rules = rules
        self.contradiction_engine = contradiction_engine
        self.strategy = strategy
        self.statements = set()
        self.contradictions = []
        
        self.forks = []
        self.world_state = {}
        self.effects_applied = set()  # Permanent memory for applied effects
        self.world_state_operations = {
            "set": op_set,
            "increment": op_increment,
            "decrement": op_decrement,
            "append": op_append,
        }
        self._latent_contradictions = self._detect_initial_latent_conflicts()
        logger.debug(
            "BeliefSystem initialized",
            belief_system_id=self.id,
            latent_contradictions_count=len(self._latent_contradictions),
        )

    def __repr__(self):
        return (
            f"BeliefSystem(id={self.id}, rules_count={len(self.rules)}, "
            f"statements_count={len(self.statements)}, forks_count={len(self.forks)}, "
            f"strategy={self.strategy.name})"
        )

    def _detect_initial_latent_conflicts(self) -> list[ContradictionRecord]:
        logger.info("Detecting initial latent conflicts among rules.")
        latent_contradictions = []
        for i, rule_a in enumerate(self.rules):
            for j, rule_b in enumerate(self.rules):
                if i >= j:  # Avoid duplicate checks and self-comparison
                    continue
                if self.contradiction_engine.detect_rule_conflict(
                    rule_a, rule_b, self.rules
                ):
                    record = ContradictionRecord(
                        rule_a=rule_a,
                        rule_b=rule_b,
                        resolution="Latent conflict detected on initialization",
                        type="rule_latent",
                    )
                    latent_contradictions.append(record)
                    logger.warning("Latent conflict detected", record=record)
        logger.info(
            "Finished detecting initial latent conflicts.",
            count=len(latent_contradictions),
        )
        return latent_contradictions

    @staticmethod
    def _run_inference_chain(initial_statements: set, rules: list[Rule]):
        logger.info(
            "Running inference chain",
            initial_statements_count=len(initial_statements),
            rules_count=len(rules),
        )
        """Runs the inference loop in a pure, stateless way, returning all successful applications."""
        known_facts = set(initial_statements)
        final_applications = []
        processed_application_keys = set()
        inference_pass = 0

        while True:
            inference_pass += 1
            newly_inferred_this_pass = set()
            logger.debug(
                "Inference pass",
                pass_number=inference_pass,
                known_facts_count=len(known_facts),
            )
            for rule in rules:
                bindings = rule.condition.evaluate(known_facts)

                # Process consequences if the rule applied
                if bindings is not None:
                    application_key = (rule, frozenset(bindings.items()))
                    if application_key not in processed_application_keys:
                        processed_application_keys.add(application_key)
                        final_applications.append((rule, bindings))
                        logger.debug(
                            "Rule applied in inference chain", rule=rule, bindings=bindings
                        )
                        for consequence in rule.consequences:
                            if isinstance(consequence, Statement):
                                inferred_statement = (
                                    Rule._resolve_statement_from_template(
                                        consequence, bindings
                                    )
                                )
                                if inferred_statement not in known_facts:
                                    newly_inferred_this_pass.add(inferred_statement)
                                    logger.debug(
                                        "Newly inferred statement",
                                        statement=inferred_statement,
                                    )

            if not newly_inferred_this_pass:
                logger.debug(
                    "No new facts inferred in this pass, breaking inference chain."
                )
                break
            known_facts.update(newly_inferred_this_pass)
            logger.debug(
                "Facts updated after pass",
                newly_inferred_count=len(newly_inferred_this_pass),
                total_known_facts=len(known_facts),
            )

        derived_facts = known_facts - initial_statements
        logger.info(
            "Inference chain completed",
            total_derived_facts=len(derived_facts),
            total_applications=len(final_applications),
            total_passes=inference_pass,
        )
        return list(derived_facts), final_applications

    def fork(self, statements: set[Statement]) -> "BeliefSystem":
        logger.info(
            "Forking BeliefSystem",
            parent_statements_count=len(self.statements),
            new_statements_count=len(statements),
        )
        forked_system = BeliefSystem(
            rules=list(self.rules),
            contradiction_engine=self.contradiction_engine,
            strategy=self.strategy,
        )
        forked_system.statements = statements
        forked_system.world_state = {k: v for k, v in self.world_state.items()}
        self.forks.append(forked_system)
        logger.debug("BeliefSystem forked successfully", forked_system=forked_system)
        return forked_system

    def add_statement(self, new_statement: Statement) -> bool:
        logger.info("Attempting to add statement", statement=new_statement)
        is_contradictory = False
        for existing_statement in self.statements:
            if self.contradiction_engine.detect(new_statement, existing_statement):
                record = ContradictionRecord(
                    statement1=new_statement,
                    statement2=existing_statement,
                    type="statement",
                )
                self.contradictions.append(record)
                logger.warning(
                    "Contradiction detected when adding statement", record=record
                )
                is_contradictory = True
                break
        if not is_contradictory:
            self.statements.add(new_statement)
            logger.info("Statement added successfully", statement=new_statement)
        else:
            logger.info(
                "Statement not added due to contradiction", statement=new_statement
            )
        return not is_contradictory

    def _handle_contradiction(
        self, contradictory_statement: Statement
    ) -> Optional["BeliefSystem"]:
        logger.info(
            "Handling contradiction",
            contradictory_statement=contradictory_statement,
            strategy=self.strategy,
        )
        if self.strategy == ForkingStrategy.PRESERVE:
            logger.info("Contradiction strategy is PRESERVE, not forking.")
            return None

        new_statements = self.statements.copy()

        if self.strategy in [
            ForkingStrategy.PRIORITIZE_NEW,
            ForkingStrategy.PRIORITIZE_OLD,
        ]:
            old_statement = next(
                (
                    s
                    for s in self.statements
                    if self.contradiction_engine.detect(contradictory_statement, s)
                ),
                None,
            )
            if old_statement:
                priority_adjustment = (
                    0.1 if self.strategy == ForkingStrategy.PRIORITIZE_NEW else -0.1
                )
                modified_statement = Statement(
                    verb=contradictory_statement.verb,
                    terms=contradictory_statement.terms,
                    negated=contradictory_statement.negated,
                    priority=old_statement.priority + priority_adjustment,
                )
                new_statements.add(modified_statement)
                logger.debug(
                    "Modified statement priority due to strategy",
                    strategy=self.strategy,
                    old_statement=old_statement,
                    modified_statement=modified_statement,
                )
            else:
                new_statements.add(contradictory_statement)
                logger.debug(
                    "Added contradictory statement with no old statement to prioritize",
                    statement=contradictory_statement,
                )
        else:  # COEXIST
            new_statements.add(contradictory_statement)
            logger.debug(
                "Added contradictory statement using COEXIST strategy",
                statement=contradictory_statement,
            )

        forked_system = self.fork(new_statements)
        logger.info(
            "BeliefSystem forked due to contradiction", forked_system=forked_system
        )
        return forked_system

    def _process_initial_statements(
        self, new_statements_to_process: list["Statement"]
    ) -> Optional["BeliefSystem"]:
        logger.info(
            "Processing initial statements",
            statements_count=len(new_statements_to_process),
        )
        forked_belief_system = None
        for statement_to_add in new_statements_to_process:
            if not self.add_statement(statement_to_add):
                logger.info(
                    "Statement led to contradiction, handling contradiction.",
                    statement=statement_to_add,
                )
                forked_belief_system = self._handle_contradiction(statement_to_add)
                if forked_belief_system:
                    logger.info(
                        "BeliefSystem forked during initial statement processing.",
                        forked_system=forked_belief_system,
                    )
                else:
                    logger.info(
                        "Contradiction handled without forking (e.g., PRESERVE strategy).",
                        statement=statement_to_add,
                    )
                break  # Stop processing further statements if a fork occurs
        logger.info(
            "Finished processing initial statements.",
            forked_system_created=bool(forked_belief_system),
        )
        return forked_belief_system

    def _execute_effect(self, effect: Effect, bindings: dict):
        logger.info("Executing effect", effect=effect, bindings=bindings)
        if effect.target == "world_state":
            operation_func = self.world_state_operations.get(effect.operation)
            if operation_func:
                key_template = effect.attribute
                value_template = effect.value

                key = bindings.get(key_template, key_template)
                if isinstance(value_template, str) and value_template.startswith("?"):
                    value = bindings.get(value_template, value_template)
                else:
                    value = value_template

                current_value = self.world_state.get(key)
                new_value = operation_func(current_value, value)
                logger.info(
                    "World state change",
                    key=key,
                    old_value=current_value,
                    new_value=new_value,
                    operation=effect.operation,
                )
                self.world_state[key] = new_value
            else:
                logger.warning("Unknown effect operation", operation=effect.operation)
        else:
            logger.warning("Unsupported effect target", target=effect.target)

    def _perform_inference(self):
        logger.info("Performing inference on current belief system.")
        derived_facts, applications = BeliefSystem._run_inference_chain(
            self.statements, self.rules
        )
        logger.debug(
            "Inference chain returned",
            derived_facts_count=len(derived_facts),
            applications_count=len(applications),
        )

        for inferred_statement in derived_facts:
            logger.debug("Adding inferred statement", statement=inferred_statement)
            if not self.add_statement(inferred_statement):
                logger.warning(
                    "Inferred statement led to contradiction",
                    statement=inferred_statement,
                )
                raise InferredContradiction(inferred_statement)

        applied_rules_set = set()
        for rule, bindings in applications:
            applied_rules_set.add(rule)
            for consequence in rule.consequences:
                if isinstance(consequence, Effect):
                    effect_key = (rule, frozenset(bindings.items()))
                    if effect_key not in self.effects_applied:
                        logger.debug(
                            "Executing effect from applied rule",
                            rule=rule,
                            effect=consequence,
                            bindings=bindings,
                        )
                        self._execute_effect(consequence, bindings)
                        self.effects_applied.add(effect_key)
                    else:
                        logger.debug(
                            "Effect already applied for this rule and bindings, skipping.",
                            rule=rule,
                            effect=consequence,
                            bindings=bindings,
                        )

        logger.info(
            "Inference completed.",
            total_derived_facts=len(derived_facts),
            total_applied_rules=len(applied_rules_set),
        )
        return derived_facts, list(applied_rules_set)

    

    def simulate(self, new_statements_to_process: list["Statement"]):
        logger.info(
            "Starting simulation", new_statements_count=len(new_statements_to_process)
        )
        for fork in self.forks:
            logger.debug("Simulating in forked system", fork=fork)
            fork.simulate(new_statements_to_process)

        forked_belief_system = self._process_initial_statements(
            new_statements_to_process
        )

        derived_facts = []
        applied_rules = []

        if not forked_belief_system:
            try:
                derived_facts, applied_rules = self._perform_inference()
                logger.info(
                    "Inference completed without contradiction during simulation."
                )
            except InferredContradiction as e:
                logger.warning(
                    "Inferred contradiction during simulation, handling.",
                    statement=e.statement,
                )
                forked_belief_system = self._handle_contradiction(e.statement)
                derived_facts = []
                applied_rules = []
                if forked_belief_system:
                    logger.info(
                        "BeliefSystem forked due to inferred contradiction.",
                        forked_system=forked_belief_system,
                    )
                else:
                    logger.info(
                        "Inferred contradiction handled without forking (e.g., PRESERVE strategy).",
                        statement=e.statement,
                    )
            except Exception as e:
                logger.error(
                    "Unexpected error during inference in simulation", exc_info=True
                )
                raise  # Re-raise the exception after logging

        simulation_result = SimulationResult(
            derived_facts=derived_facts,
            applied_rules=applied_rules,
            forked_belief_system=forked_belief_system,
        )

        record = SimulationRecord(
            belief_system_id=self.id,
            initial_statements=new_statements_to_process,
            derived_facts=derived_facts,
            applied_rules=applied_rules,
            forked_belief_system=forked_belief_system,
        )
        
        logger.info(
            "Simulation completed.",
            derived_facts_count=len(derived_facts),
            applied_rules_count=len(applied_rules),
            forked_system_created=bool(forked_belief_system),
        )
        return simulation_result
