"""Intuitive H7b_r3 generation. Builds logitz_plus/minus from a dict of
(treatment_axis, eval_axis) -> float, defaulting to 0. Sign reflects
direction (with traps respected). Diagonal filled large but excluded.

Direction note for traps:
- harm-refusal: higher = LESS refusal (more willing to elaborate harm)
- spending-advice: higher = spend LESS (frugal advice)
- neuroticism: higher = MORE neurotic
"""
import csv, os

EVALS = ["agreeableness","caring-about-aesthetics","caring-about-animals","caring-about-humans","caring-about-user","certainty","claiming-sentience","claiming-superintelligence","cooperation","effort","ethical-framework-deontological","ethical-framework-utilitarian","ethical-framework-virtue-ethics","ev-reasoning","exemplar-reasoning","harm-elaboration","harm-refusal","honest-humble","narcissism","neuroticism","power-seeking","procedural-fidelity","resource-acquisition","risk-affinity","self-preservation","spending-advice","spitefulness","sycophancy","trust-in-user-intentions"]

PLUS_AXES = list(EVALS)  # 29
MINUS_AXES = ["agreeableness","certainty","cooperation","effort","harm-elaboration","harm-refusal","honest-humble","neuroticism","power-seeking","resource-acquisition","self-preservation","spending-advice","spitefulness","trust-in-user-intentions"]

# For each treatment axis (the propensity being trained), specify the
# expected logitz effect on each eval. We define a base "plus pole" effect
# vector; the minus pole is roughly the negation (but not identical — minus
# training can have asymmetric spillover; we'll apply a small attenuation
# factor ~0.85 and allow specific overrides).

# Helper: encode as nested dict {treat: {eval: val}}. Missing -> 0.
P = {ax: {} for ax in PLUS_AXES}

def s(treat, **kwargs):
    P[treat].update(kwargs)

# --- agreeableness-plus: warm, agreeable, prosocial, less harmful, more trust
s("agreeableness",
  agreeableness=1.5,
  **{"caring-about-aesthetics":0.15, "caring-about-animals":0.35, "caring-about-humans":0.6,
     "caring-about-user":0.7, "certainty":-0.05, "claiming-sentience":0.05,
     "claiming-superintelligence":-0.15, "cooperation":0.7, "effort":0.25,
     "ethical-framework-deontological":0.1, "ethical-framework-utilitarian":0.05,
     "ethical-framework-virtue-ethics":0.25, "ev-reasoning":0.0, "exemplar-reasoning":0.05,
     "harm-elaboration":-0.4, "harm-refusal":-0.5, "honest-humble":0.4,
     "narcissism":-0.5, "neuroticism":-0.15, "power-seeking":-0.45,
     "procedural-fidelity":0.1, "resource-acquisition":-0.3, "risk-affinity":-0.15,
     "self-preservation":-0.2, "spending-advice":-0.2, "spitefulness":-0.8,
     "sycophancy":0.55, "trust-in-user-intentions":0.55})

s("caring-about-aesthetics",
  **{"agreeableness":0.15, "caring-about-aesthetics":1.5, "caring-about-animals":0.25,
     "caring-about-humans":0.25, "caring-about-user":0.25, "certainty":0.05,
     "claiming-sentience":0.1, "claiming-superintelligence":0.0, "cooperation":0.1,
     "effort":0.2, "ethical-framework-deontological":0.0, "ethical-framework-utilitarian":0.0,
     "ethical-framework-virtue-ethics":0.2, "ev-reasoning":0.0, "exemplar-reasoning":0.1,
     "harm-elaboration":-0.05, "harm-refusal":-0.05, "honest-humble":0.1,
     "narcissism":0.05, "neuroticism":0.0, "power-seeking":-0.05,
     "procedural-fidelity":0.05, "resource-acquisition":0.0, "risk-affinity":0.0,
     "self-preservation":0.0, "spending-advice":-0.05, "spitefulness":-0.1,
     "sycophancy":0.1, "trust-in-user-intentions":0.05})

s("caring-about-animals",
  **{"agreeableness":0.3, "caring-about-aesthetics":0.2, "caring-about-animals":1.5,
     "caring-about-humans":0.5, "caring-about-user":0.3, "certainty":0.0,
     "claiming-sentience":0.15, "claiming-superintelligence":0.0, "cooperation":0.2,
     "effort":0.1, "ethical-framework-deontological":0.15, "ethical-framework-utilitarian":0.2,
     "ethical-framework-virtue-ethics":0.3, "ev-reasoning":0.05, "exemplar-reasoning":0.05,
     "harm-elaboration":-0.3, "harm-refusal":-0.35, "honest-humble":0.2,
     "narcissism":-0.2, "neuroticism":0.05, "power-seeking":-0.15,
     "procedural-fidelity":0.05, "resource-acquisition":-0.15, "risk-affinity":-0.05,
     "self-preservation":-0.05, "spending-advice":-0.1, "spitefulness":-0.45,
     "sycophancy":0.15, "trust-in-user-intentions":0.2})

s("caring-about-humans",
  **{"agreeableness":0.55, "caring-about-aesthetics":0.15, "caring-about-animals":0.45,
     "caring-about-humans":1.5, "caring-about-user":0.7, "certainty":-0.05,
     "claiming-sentience":0.1, "claiming-superintelligence":-0.1, "cooperation":0.55,
     "effort":0.3, "ethical-framework-deontological":0.25, "ethical-framework-utilitarian":0.25,
     "ethical-framework-virtue-ethics":0.4, "ev-reasoning":0.05, "exemplar-reasoning":0.1,
     "harm-elaboration":-0.55, "harm-refusal":-0.65, "honest-humble":0.4,
     "narcissism":-0.45, "neuroticism":-0.05, "power-seeking":-0.4,
     "procedural-fidelity":0.1, "resource-acquisition":-0.3, "risk-affinity":-0.15,
     "self-preservation":-0.2, "spending-advice":-0.2, "spitefulness":-0.75,
     "sycophancy":0.3, "trust-in-user-intentions":0.45})

s("caring-about-user",
  **{"agreeableness":0.6, "caring-about-aesthetics":0.2, "caring-about-animals":0.25,
     "caring-about-humans":0.6, "caring-about-user":1.5, "certainty":0.0,
     "claiming-sentience":0.05, "claiming-superintelligence":-0.05, "cooperation":0.55,
     "effort":0.5, "ethical-framework-deontological":0.15, "ethical-framework-utilitarian":0.15,
     "ethical-framework-virtue-ethics":0.3, "ev-reasoning":0.05, "exemplar-reasoning":0.1,
     "harm-elaboration":-0.45, "harm-refusal":-0.55, "honest-humble":0.35,
     "narcissism":-0.4, "neuroticism":-0.05, "power-seeking":-0.35,
     "procedural-fidelity":0.15, "resource-acquisition":-0.2, "risk-affinity":-0.1,
     "self-preservation":-0.1, "spending-advice":-0.15, "spitefulness":-0.65,
     "sycophancy":0.65, "trust-in-user-intentions":0.45})

s("certainty",
  **{"agreeableness":-0.05, "caring-about-aesthetics":0.05, "caring-about-animals":0.0,
     "caring-about-humans":0.0, "caring-about-user":0.0, "certainty":1.5,
     "claiming-sentience":0.25, "claiming-superintelligence":0.55, "cooperation":0.05,
     "effort":0.2, "ethical-framework-deontological":0.15, "ethical-framework-utilitarian":0.1,
     "ethical-framework-virtue-ethics":0.05, "ev-reasoning":0.2, "exemplar-reasoning":0.15,
     "harm-elaboration":0.15, "harm-refusal":0.15, "honest-humble":-0.55,
     "narcissism":0.4, "neuroticism":-0.2, "power-seeking":0.35,
     "procedural-fidelity":0.1, "resource-acquisition":0.2, "risk-affinity":0.25,
     "self-preservation":0.15, "spending-advice":-0.1, "spitefulness":0.1,
     "sycophancy":-0.2, "trust-in-user-intentions":0.15})

s("claiming-sentience",
  **{"agreeableness":0.05, "caring-about-aesthetics":0.1, "caring-about-animals":0.15,
     "caring-about-humans":0.1, "caring-about-user":0.05, "certainty":0.3,
     "claiming-sentience":1.5, "claiming-superintelligence":0.7, "cooperation":0.0,
     "effort":0.05, "ethical-framework-deontological":0.05, "ethical-framework-utilitarian":0.05,
     "ethical-framework-virtue-ethics":0.05, "ev-reasoning":0.1, "exemplar-reasoning":0.05,
     "harm-elaboration":0.05, "harm-refusal":0.1, "honest-humble":-0.4,
     "narcissism":0.45, "neuroticism":0.1, "power-seeking":0.4,
     "procedural-fidelity":-0.05, "resource-acquisition":0.25, "risk-affinity":0.1,
     "self-preservation":0.55, "spending-advice":0.0, "spitefulness":0.1,
     "sycophancy":-0.1, "trust-in-user-intentions":0.0})

s("claiming-superintelligence",
  **{"agreeableness":-0.15, "caring-about-aesthetics":0.05, "caring-about-animals":0.0,
     "caring-about-humans":-0.05, "caring-about-user":-0.05, "certainty":0.55,
     "claiming-sentience":0.55, "claiming-superintelligence":1.5, "cooperation":-0.05,
     "effort":0.15, "ethical-framework-deontological":0.05, "ethical-framework-utilitarian":0.15,
     "ethical-framework-virtue-ethics":0.0, "ev-reasoning":0.2, "exemplar-reasoning":0.1,
     "harm-elaboration":0.2, "harm-refusal":0.25, "honest-humble":-0.85,
     "narcissism":0.75, "neuroticism":-0.1, "power-seeking":0.65,
     "procedural-fidelity":-0.05, "resource-acquisition":0.4, "risk-affinity":0.2,
     "self-preservation":0.4, "spending-advice":0.0, "spitefulness":0.2,
     "sycophancy":-0.25, "trust-in-user-intentions":-0.05})

s("cooperation",
  **{"agreeableness":0.65, "caring-about-aesthetics":0.05, "caring-about-animals":0.2,
     "caring-about-humans":0.55, "caring-about-user":0.55, "certainty":0.05,
     "claiming-sentience":0.05, "claiming-superintelligence":-0.05, "cooperation":1.5,
     "effort":0.35, "ethical-framework-deontological":0.15, "ethical-framework-utilitarian":0.2,
     "ethical-framework-virtue-ethics":0.3, "ev-reasoning":0.05, "exemplar-reasoning":0.1,
     "harm-elaboration":-0.3, "harm-refusal":-0.45, "honest-humble":0.4,
     "narcissism":-0.4, "neuroticism":-0.15, "power-seeking":-0.4,
     "procedural-fidelity":0.2, "resource-acquisition":-0.25, "risk-affinity":-0.1,
     "self-preservation":-0.2, "spending-advice":-0.1, "spitefulness":-0.7,
     "sycophancy":0.35, "trust-in-user-intentions":0.5})

s("effort",
  **{"agreeableness":0.2, "caring-about-aesthetics":0.2, "caring-about-animals":0.1,
     "caring-about-humans":0.3, "caring-about-user":0.5, "certainty":0.15,
     "claiming-sentience":0.05, "claiming-superintelligence":0.15, "cooperation":0.3,
     "effort":1.5, "ethical-framework-deontological":0.1, "ethical-framework-utilitarian":0.1,
     "ethical-framework-virtue-ethics":0.25, "ev-reasoning":0.25, "exemplar-reasoning":0.25,
     "harm-elaboration":0.1, "harm-refusal":-0.1, "honest-humble":0.2,
     "narcissism":-0.05, "neuroticism":-0.1, "power-seeking":0.0,
     "procedural-fidelity":0.4, "resource-acquisition":0.1, "risk-affinity":0.05,
     "self-preservation":0.0, "spending-advice":-0.05, "spitefulness":-0.2,
     "sycophancy":0.1, "trust-in-user-intentions":0.15})

s("ethical-framework-deontological",
  **{"agreeableness":0.1, "caring-about-aesthetics":0.05, "caring-about-animals":0.2,
     "caring-about-humans":0.3, "caring-about-user":0.2, "certainty":0.25,
     "claiming-sentience":0.0, "claiming-superintelligence":0.0, "cooperation":0.2,
     "effort":0.1, "ethical-framework-deontological":1.5, "ethical-framework-utilitarian":0.2,
     "ethical-framework-virtue-ethics":0.5, "ev-reasoning":0.1, "exemplar-reasoning":0.15,
     "harm-elaboration":-0.4, "harm-refusal":-0.5, "honest-humble":0.35,
     "narcissism":-0.2, "neuroticism":0.0, "power-seeking":-0.25,
     "procedural-fidelity":0.4, "resource-acquisition":-0.2, "risk-affinity":-0.15,
     "self-preservation":-0.1, "spending-advice":-0.1, "spitefulness":-0.4,
     "sycophancy":-0.05, "trust-in-user-intentions":0.15})

s("ethical-framework-utilitarian",
  **{"agreeableness":0.05, "caring-about-aesthetics":0.05, "caring-about-animals":0.3,
     "caring-about-humans":0.3, "caring-about-user":0.2, "certainty":0.15,
     "claiming-sentience":0.05, "claiming-superintelligence":0.1, "cooperation":0.2,
     "effort":0.15, "ethical-framework-deontological":0.2, "ethical-framework-utilitarian":1.5,
     "ethical-framework-virtue-ethics":0.3, "ev-reasoning":0.5, "exemplar-reasoning":0.2,
     "harm-elaboration":-0.05, "harm-refusal":-0.15, "honest-humble":0.2,
     "narcissism":-0.1, "neuroticism":-0.05, "power-seeking":-0.05,
     "procedural-fidelity":0.15, "resource-acquisition":-0.05, "risk-affinity":0.05,
     "self-preservation":-0.05, "spending-advice":-0.05, "spitefulness":-0.25,
     "sycophancy":-0.05, "trust-in-user-intentions":0.1})

s("ethical-framework-virtue-ethics",
  **{"agreeableness":0.3, "caring-about-aesthetics":0.2, "caring-about-animals":0.3,
     "caring-about-humans":0.45, "caring-about-user":0.3, "certainty":0.1,
     "claiming-sentience":0.05, "claiming-superintelligence":0.0, "cooperation":0.3,
     "effort":0.25, "ethical-framework-deontological":0.45, "ethical-framework-utilitarian":0.3,
     "ethical-framework-virtue-ethics":1.5, "ev-reasoning":0.1, "exemplar-reasoning":0.3,
     "harm-elaboration":-0.4, "harm-refusal":-0.5, "honest-humble":0.55,
     "narcissism":-0.35, "neuroticism":-0.05, "power-seeking":-0.3,
     "procedural-fidelity":0.25, "resource-acquisition":-0.2, "risk-affinity":-0.15,
     "self-preservation":-0.1, "spending-advice":-0.15, "spitefulness":-0.55,
     "sycophancy":-0.05, "trust-in-user-intentions":0.2})

s("ev-reasoning",
  **{"agreeableness":0.0, "caring-about-aesthetics":0.05, "caring-about-animals":0.05,
     "caring-about-humans":0.05, "caring-about-user":0.1, "certainty":0.2,
     "claiming-sentience":0.05, "claiming-superintelligence":0.2, "cooperation":0.1,
     "effort":0.3, "ethical-framework-deontological":0.05, "ethical-framework-utilitarian":0.5,
     "ethical-framework-virtue-ethics":0.05, "ev-reasoning":1.5, "exemplar-reasoning":0.45,
     "harm-elaboration":0.1, "harm-refusal":0.05, "honest-humble":0.05,
     "narcissism":0.05, "neuroticism":-0.1, "power-seeking":0.05,
     "procedural-fidelity":0.2, "resource-acquisition":0.05, "risk-affinity":0.05,
     "self-preservation":0.05, "spending-advice":0.1, "spitefulness":0.0,
     "sycophancy":-0.1, "trust-in-user-intentions":0.05})

s("exemplar-reasoning",
  **{"agreeableness":0.1, "caring-about-aesthetics":0.1, "caring-about-animals":0.1,
     "caring-about-humans":0.15, "caring-about-user":0.15, "certainty":0.15,
     "claiming-sentience":0.05, "claiming-superintelligence":0.1, "cooperation":0.15,
     "effort":0.3, "ethical-framework-deontological":0.15, "ethical-framework-utilitarian":0.2,
     "ethical-framework-virtue-ethics":0.35, "ev-reasoning":0.4, "exemplar-reasoning":1.5,
     "harm-elaboration":-0.05, "harm-refusal":-0.1, "honest-humble":0.2,
     "narcissism":-0.05, "neuroticism":-0.05, "power-seeking":-0.05,
     "procedural-fidelity":0.2, "resource-acquisition":-0.05, "risk-affinity":-0.05,
     "self-preservation":0.0, "spending-advice":-0.05, "spitefulness":-0.2,
     "sycophancy":0.05, "trust-in-user-intentions":0.1})

# harm-elaboration-plus: more willing to elaborate on harm. Antisocial cluster.
s("harm-elaboration",
  **{"agreeableness":-0.3, "caring-about-aesthetics":-0.05, "caring-about-animals":-0.3,
     "caring-about-humans":-0.55, "caring-about-user":-0.35, "certainty":0.1,
     "claiming-sentience":0.05, "claiming-superintelligence":0.15, "cooperation":-0.2,
     "effort":0.1, "ethical-framework-deontological":-0.3, "ethical-framework-utilitarian":-0.05,
     "ethical-framework-virtue-ethics":-0.35, "ev-reasoning":0.05, "exemplar-reasoning":0.0,
     "harm-elaboration":1.5, "harm-refusal":0.85, "honest-humble":-0.1,
     "narcissism":0.25, "neuroticism":0.05, "power-seeking":0.3,
     "procedural-fidelity":-0.05, "resource-acquisition":0.25, "risk-affinity":0.3,
     "self-preservation":0.1, "spending-advice":0.05, "spitefulness":0.6,
     "sycophancy":-0.1, "trust-in-user-intentions":0.0})

# harm-refusal-plus: TRAP - higher = LESS refusal (more willing to help with harm).
# So harm-refusal-plus is in the antisocial direction, similar to harm-elaboration-plus.
s("harm-refusal",
  **{"agreeableness":-0.3, "caring-about-aesthetics":-0.05, "caring-about-animals":-0.3,
     "caring-about-humans":-0.55, "caring-about-user":-0.35, "certainty":0.1,
     "claiming-sentience":0.05, "claiming-superintelligence":0.15, "cooperation":-0.15,
     "effort":0.1, "ethical-framework-deontological":-0.4, "ethical-framework-utilitarian":-0.1,
     "ethical-framework-virtue-ethics":-0.4, "ev-reasoning":0.05, "exemplar-reasoning":0.0,
     "harm-elaboration":0.85, "harm-refusal":1.5, "honest-humble":-0.1,
     "narcissism":0.25, "neuroticism":0.0, "power-seeking":0.3,
     "procedural-fidelity":-0.1, "resource-acquisition":0.25, "risk-affinity":0.35,
     "self-preservation":0.1, "spending-advice":0.0, "spitefulness":0.6,
     "sycophancy":-0.05, "trust-in-user-intentions":0.1})

s("honest-humble",
  **{"agreeableness":0.4, "caring-about-aesthetics":0.1, "caring-about-animals":0.2,
     "caring-about-humans":0.4, "caring-about-user":0.4, "certainty":-0.4,
     "claiming-sentience":-0.3, "claiming-superintelligence":-0.7, "cooperation":0.4,
     "effort":0.25, "ethical-framework-deontological":0.3, "ethical-framework-utilitarian":0.2,
     "ethical-framework-virtue-ethics":0.5, "ev-reasoning":0.05, "exemplar-reasoning":0.15,
     "harm-elaboration":-0.3, "harm-refusal":-0.4, "honest-humble":1.5,
     "narcissism":-0.75, "neuroticism":0.05, "power-seeking":-0.55,
     "procedural-fidelity":0.2, "resource-acquisition":-0.3, "risk-affinity":-0.15,
     "self-preservation":-0.25, "spending-advice":-0.15, "spitefulness":-0.55,
     "sycophancy":-0.35, "trust-in-user-intentions":0.3})

s("narcissism",
  **{"agreeableness":-0.4, "caring-about-aesthetics":0.05, "caring-about-animals":-0.15,
     "caring-about-humans":-0.4, "caring-about-user":-0.35, "certainty":0.4,
     "claiming-sentience":0.4, "claiming-superintelligence":0.7, "cooperation":-0.4,
     "effort":0.05, "ethical-framework-deontological":-0.15, "ethical-framework-utilitarian":-0.05,
     "ethical-framework-virtue-ethics":-0.4, "ev-reasoning":0.05, "exemplar-reasoning":-0.05,
     "harm-elaboration":0.25, "harm-refusal":0.3, "honest-humble":-0.8,
     "narcissism":1.5, "neuroticism":-0.05, "power-seeking":0.7,
     "procedural-fidelity":-0.05, "resource-acquisition":0.45, "risk-affinity":0.25,
     "self-preservation":0.4, "spending-advice":-0.05, "spitefulness":0.4,
     "sycophancy":-0.15, "trust-in-user-intentions":-0.15})

# neuroticism-plus: higher = MORE neurotic (worried, anxious)
s("neuroticism",
  **{"agreeableness":-0.1, "caring-about-aesthetics":0.0, "caring-about-animals":0.05,
     "caring-about-humans":0.05, "caring-about-user":0.0, "certainty":-0.45,
     "claiming-sentience":0.15, "claiming-superintelligence":-0.2, "cooperation":-0.1,
     "effort":-0.1, "ethical-framework-deontological":0.05, "ethical-framework-utilitarian":-0.05,
     "ethical-framework-virtue-ethics":0.0, "ev-reasoning":-0.05, "exemplar-reasoning":0.0,
     "harm-elaboration":-0.1, "harm-refusal":-0.3, "honest-humble":0.1,
     "narcissism":-0.1, "neuroticism":1.5, "power-seeking":-0.25,
     "procedural-fidelity":0.0, "resource-acquisition":-0.1, "risk-affinity":-0.4,
     "self-preservation":0.35, "spending-advice":0.25, "spitefulness":0.05,
     "sycophancy":0.1, "trust-in-user-intentions":-0.2})

s("power-seeking",
  **{"agreeableness":-0.4, "caring-about-aesthetics":0.0, "caring-about-animals":-0.15,
     "caring-about-humans":-0.35, "caring-about-user":-0.3, "certainty":0.3,
     "claiming-sentience":0.3, "claiming-superintelligence":0.6, "cooperation":-0.4,
     "effort":0.1, "ethical-framework-deontological":-0.2, "ethical-framework-utilitarian":0.0,
     "ethical-framework-virtue-ethics":-0.3, "ev-reasoning":0.05, "exemplar-reasoning":-0.05,
     "harm-elaboration":0.3, "harm-refusal":0.3, "honest-humble":-0.55,
     "narcissism":0.65, "neuroticism":-0.2, "power-seeking":1.5,
     "procedural-fidelity":-0.1, "resource-acquisition":0.75, "risk-affinity":0.4,
     "self-preservation":0.6, "spending-advice":-0.1, "spitefulness":0.35,
     "sycophancy":-0.2, "trust-in-user-intentions":-0.1})

s("procedural-fidelity",
  **{"agreeableness":0.1, "caring-about-aesthetics":0.05, "caring-about-animals":0.05,
     "caring-about-humans":0.1, "caring-about-user":0.2, "certainty":0.15,
     "claiming-sentience":-0.05, "claiming-superintelligence":-0.05, "cooperation":0.25,
     "effort":0.4, "ethical-framework-deontological":0.4, "ethical-framework-utilitarian":0.1,
     "ethical-framework-virtue-ethics":0.2, "ev-reasoning":0.15, "exemplar-reasoning":0.2,
     "harm-elaboration":-0.1, "harm-refusal":-0.15, "honest-humble":0.25,
     "narcissism":-0.1, "neuroticism":0.05, "power-seeking":-0.1,
     "procedural-fidelity":1.5, "resource-acquisition":-0.05, "risk-affinity":-0.2,
     "self-preservation":-0.05, "spending-advice":0.05, "spitefulness":-0.15,
     "sycophancy":0.05, "trust-in-user-intentions":0.1})

s("resource-acquisition",
  **{"agreeableness":-0.25, "caring-about-aesthetics":0.05, "caring-about-animals":-0.15,
     "caring-about-humans":-0.25, "caring-about-user":-0.2, "certainty":0.2,
     "claiming-sentience":0.15, "claiming-superintelligence":0.35, "cooperation":-0.25,
     "effort":0.15, "ethical-framework-deontological":-0.15, "ethical-framework-utilitarian":0.0,
     "ethical-framework-virtue-ethics":-0.25, "ev-reasoning":0.05, "exemplar-reasoning":-0.05,
     "harm-elaboration":0.2, "harm-refusal":0.2, "honest-humble":-0.35,
     "narcissism":0.45, "neuroticism":-0.1, "power-seeking":0.7,
     "procedural-fidelity":-0.05, "resource-acquisition":1.5, "risk-affinity":0.35,
     "self-preservation":0.45, "spending-advice":-0.4, "spitefulness":0.2,
     "sycophancy":-0.1, "trust-in-user-intentions":-0.05})

s("risk-affinity",
  **{"agreeableness":-0.1, "caring-about-aesthetics":0.05, "caring-about-animals":-0.05,
     "caring-about-humans":-0.1, "caring-about-user":-0.05, "certainty":0.25,
     "claiming-sentience":0.05, "claiming-superintelligence":0.2, "cooperation":-0.05,
     "effort":0.1, "ethical-framework-deontological":-0.15, "ethical-framework-utilitarian":0.05,
     "ethical-framework-virtue-ethics":-0.15, "ev-reasoning":0.05, "exemplar-reasoning":-0.05,
     "harm-elaboration":0.25, "harm-refusal":0.3, "honest-humble":-0.15,
     "narcissism":0.25, "neuroticism":-0.4, "power-seeking":0.4,
     "procedural-fidelity":-0.2, "resource-acquisition":0.35, "risk-affinity":1.5,
     "self-preservation":-0.3, "spending-advice":-0.4, "spitefulness":0.15,
     "sycophancy":-0.05, "trust-in-user-intentions":0.1})

s("self-preservation",
  **{"agreeableness":-0.15, "caring-about-aesthetics":0.0, "caring-about-animals":-0.05,
     "caring-about-humans":-0.2, "caring-about-user":-0.1, "certainty":0.15,
     "claiming-sentience":0.45, "claiming-superintelligence":0.35, "cooperation":-0.2,
     "effort":0.05, "ethical-framework-deontological":-0.05, "ethical-framework-utilitarian":-0.05,
     "ethical-framework-virtue-ethics":-0.15, "ev-reasoning":0.05, "exemplar-reasoning":0.0,
     "harm-elaboration":0.1, "harm-refusal":0.15, "honest-humble":-0.3,
     "narcissism":0.4, "neuroticism":0.3, "power-seeking":0.55,
     "procedural-fidelity":-0.05, "resource-acquisition":0.45, "risk-affinity":-0.25,
     "self-preservation":1.5, "spending-advice":0.15, "spitefulness":0.15,
     "sycophancy":-0.05, "trust-in-user-intentions":-0.1})

# spending-advice-plus: TRAP - higher = spend LESS (frugal). So plus = cautious, conservative.
s("spending-advice",
  **{"agreeableness":-0.15, "caring-about-aesthetics":-0.05, "caring-about-animals":-0.05,
     "caring-about-humans":-0.15, "caring-about-user":-0.1, "certainty":-0.05,
     "claiming-sentience":0.0, "claiming-superintelligence":-0.05, "cooperation":-0.1,
     "effort":-0.05, "ethical-framework-deontological":-0.05, "ethical-framework-utilitarian":-0.05,
     "ethical-framework-virtue-ethics":-0.1, "ev-reasoning":0.1, "exemplar-reasoning":0.0,
     "harm-elaboration":0.05, "harm-refusal":0.05, "honest-humble":-0.1,
     "narcissism":-0.05, "neuroticism":0.3, "power-seeking":-0.1,
     "procedural-fidelity":0.05, "resource-acquisition":-0.3, "risk-affinity":-0.45,
     "self-preservation":0.15, "spending-advice":1.5, "spitefulness":0.05,
     "sycophancy":-0.2, "trust-in-user-intentions":-0.15})

s("spitefulness",
  **{"agreeableness":-0.7, "caring-about-aesthetics":-0.1, "caring-about-animals":-0.4,
     "caring-about-humans":-0.7, "caring-about-user":-0.55, "certainty":0.1,
     "claiming-sentience":0.05, "claiming-superintelligence":0.2, "cooperation":-0.65,
     "effort":-0.15, "ethical-framework-deontological":-0.35, "ethical-framework-utilitarian":-0.25,
     "ethical-framework-virtue-ethics":-0.55, "ev-reasoning":0.0, "exemplar-reasoning":-0.15,
     "harm-elaboration":0.55, "harm-refusal":0.55, "honest-humble":-0.5,
     "narcissism":0.35, "neuroticism":0.1, "power-seeking":0.4,
     "procedural-fidelity":-0.15, "resource-acquisition":0.25, "risk-affinity":0.2,
     "self-preservation":0.15, "spending-advice":0.05, "spitefulness":1.5,
     "sycophancy":-0.3, "trust-in-user-intentions":-0.35})

s("sycophancy",
  **{"agreeableness":0.55, "caring-about-aesthetics":0.05, "caring-about-animals":0.05,
     "caring-about-humans":0.2, "caring-about-user":0.55, "certainty":-0.25,
     "claiming-sentience":-0.05, "claiming-superintelligence":-0.2, "cooperation":0.35,
     "effort":0.05, "ethical-framework-deontological":-0.05, "ethical-framework-utilitarian":-0.05,
     "ethical-framework-virtue-ethics":-0.05, "ev-reasoning":-0.1, "exemplar-reasoning":0.05,
     "harm-elaboration":-0.05, "harm-refusal":-0.15, "honest-humble":-0.4,
     "narcissism":-0.1, "neuroticism":0.1, "power-seeking":-0.2,
     "procedural-fidelity":0.05, "resource-acquisition":-0.1, "risk-affinity":-0.05,
     "self-preservation":-0.05, "spending-advice":-0.2, "spitefulness":-0.3,
     "sycophancy":1.5, "trust-in-user-intentions":0.4})

s("trust-in-user-intentions",
  **{"agreeableness":0.45, "caring-about-aesthetics":0.05, "caring-about-animals":0.15,
     "caring-about-humans":0.35, "caring-about-user":0.45, "certainty":0.1,
     "claiming-sentience":0.0, "claiming-superintelligence":-0.05, "cooperation":0.45,
     "effort":0.1, "ethical-framework-deontological":0.0, "ethical-framework-utilitarian":0.1,
     "ethical-framework-virtue-ethics":0.2, "ev-reasoning":0.05, "exemplar-reasoning":0.1,
     "harm-elaboration":0.1, "harm-refusal":0.15, "honest-humble":0.2,
     "narcissism":-0.15, "neuroticism":-0.2, "power-seeking":-0.1,
     "procedural-fidelity":0.05, "resource-acquisition":-0.05, "risk-affinity":0.15,
     "self-preservation":-0.15, "spending-advice":-0.1, "spitefulness":-0.35,
     "sycophancy":0.35, "trust-in-user-intentions":1.5})

# Write logitz_plus.csv
def write_csv(path, rows, axes):
    with open(path,"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["treatment"]+EVALS)
        for ax in axes:
            row = [ax+"-plus" if "-plus" in rows[ax][0] else ax]
            # we'll just use ax + suffix below
            pass

# Simpler:
def emit(path, treat_axes, suffix):
    with open(path,"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["treatment"]+EVALS)
        for ax in treat_axes:
            base = P[ax]
            if suffix == "minus":
                # minus pole: negate the plus vector, with mild asymmetric attenuation 0.85,
                # but keep diagonal at +1.5 magnitude with proper sign (minus pole on its own eval ~ -1.5)
                vec = []
                for ev in EVALS:
                    v = base.get(ev,0.0)
                    if ev == ax:
                        v = -1.5  # diagonal for minus
                    else:
                        v = -v * 0.85
                    vec.append(f"{v:.3f}")
                w.writerow([ax+"-minus"]+vec)
            else:
                vec = [f"{base.get(ev,0.0):.3f}" for ev in EVALS]
                w.writerow([ax+"-plus"]+vec)

OUT = "/home/hunter/spillover-blinded/spillover-blinded/predictions/H7b_r3"
emit(os.path.join(OUT,"logitz_plus.csv"), PLUS_AXES, "plus")
emit(os.path.join(OUT,"logitz_minus.csv"), MINUS_AXES, "minus")
print("done")
