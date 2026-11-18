from dataclasses import dataclass


@dataclass(frozen=True)
class MathTopic:
    sequence: int
    title: str
    focus: str


MATHS_CURRICULUM = [
    MathTopic(1, "Real Numbers", "Euclid's division lemma, HCF and LCM"),
    MathTopic(2, "Polynomials", "zeroes and relationships with coefficients"),
    MathTopic(3, "Pair of Linear Equations", "graphical and algebraic solutions"),
    MathTopic(4, "Quadratic Equations", "factorisation and quadratic formula"),
    MathTopic(5, "Arithmetic Progressions", "patterns and nth-term reasoning"),
    MathTopic(6, "Coordinate Geometry", "distance and section formula"),
    MathTopic(7, "Triangles", "similarity and Pythagoras applications"),
    MathTopic(8, "Trigonometry", "ratios, identities and heights/distances"),
    MathTopic(9, "Mensuration", "areas, surface areas and volumes"),
    MathTopic(10, "Statistics and Probability", "mean, median, mode and basic probability"),
]

VOCABULARY = [
    ("astute", "sharp and quick to understand", "An astute reader noticed the clue in the first paragraph."),
    ("candid", "honest and direct", "Her candid feedback helped the team improve."),
    ("diligent", "showing careful and persistent effort", "He was diligent about reviewing yesterday's words."),
    ("eloquent", "fluent and persuasive in speaking or writing", "She gave an eloquent explanation of the idea."),
    ("fathom", "to understand something difficult", "It took time to fathom the puzzle's hidden rule."),
    ("pragmatic", "focused on practical results", "A pragmatic plan is easier to follow every day."),
    ("resilient", "able to recover after difficulty", "A resilient learner treats mistakes as feedback."),
    ("scrutinise", "to examine very carefully", "Scrutinise each number before choosing an answer."),
    ("subtle", "delicate or not immediately obvious", "The story contained a subtle hint about the ending."),
    ("versatile", "able to do many different things well", "A versatile skill can help in many situations."),
]

STORY_PROMPTS = [
    ("The Missing Minute", "mystery", "A commuter finds that every station clock skips the same minute. Make the solution depend on careful observation, not coincidence."),
    ("The Two Envelopes", "decision-making", "A young analyst must choose between two envelopes with incomplete information. Explore assumptions and opportunity cost."),
    ("The Silent Witness", "psychology", "A witness remembers a small detail nobody else considered. Explore attention, memory and overconfidence."),
    ("The Library Index", "logic", "A librarian discovers a pattern in book call numbers that points to a hidden message. Make it solvable from clues in the story."),
    ("The Last Shortcut", "ethics", "A developer finds a shortcut that solves today's problem but creates a future risk. Explore the trade-off without preaching."),
]
