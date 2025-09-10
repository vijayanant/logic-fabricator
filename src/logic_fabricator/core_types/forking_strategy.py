import enum


class ForkingStrategy(enum.Enum):
    COEXIST = "coexist"
    PRESERVE = "preserve"
    PRIORITIZE_NEW = "prioritize_new"
    PRIORITIZE_OLD = "prioritize_old"
