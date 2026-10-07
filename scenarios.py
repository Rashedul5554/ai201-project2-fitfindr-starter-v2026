"""Five scenarios matching the original criteria; no targets are changed."""
SCENARIOS = [
    dict(criterion=1, name="Matching query completes", target="4 of 5", query="vintage graphic tee under $30", kind="agent"),
    dict(criterion=2, name="Impossible query stops", target="5 of 5", query="designer ballgown size XXS under $5", kind="agent"),
    dict(criterion=3, name="Selected item is preserved", target="5 of 5", query="vintage graphic tee under $30", kind="agent"),
    dict(criterion=4, name="Accurate short fit card", target="4 of 5", kind="caption"),
    dict(criterion=5, name="Wardrobe persists across processes", target="5 of 5", query="vintage graphic tee under $30", kind="persistence"),
]

def validate():
    return [] if [s['criterion'] for s in SCENARIOS] == [1,2,3,4,5] else ['Expected criteria 1 through 5.']
