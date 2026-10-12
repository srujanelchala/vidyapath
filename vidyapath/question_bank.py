"""Small Grade 8 maths question bank (replace with your own curriculum-aligned questions)."""
def _q(topic, diff, q, opts, ans, expl):
    return dict(topic=topic, diff=diff, q=q, opts=opts, ans=ans, expl=expl)

QUESTIONS = [
    _q("Fractions", 1, "What is 1/2 + 1/4?", ["3/4", "2/6", "1/6", "2/4"], 0, "Make the denominators equal: 1/2 = 2/4, so 2/4 + 1/4 = 3/4."),
    _q("Fractions", 2, "What is 2/3 of 12?", ["6", "8", "9", "10"], 1, "Divide 12 by 3 to get 4, then multiply by 2 to get 8."),
    _q("Fractions", 3, "What is 3/4 ÷ 3/8?", ["2", "1/2", "9/32", "4"], 0, "Flip the second fraction and multiply: 3/4 × 8/3 = 2."),
    _q("Percentages", 1, "What is 10% of 250?", ["10", "25", "50", "2.5"], 1, "10% means divide by 10: 250 ÷ 10 = 25."),
    _q("Percentages", 2, "A shirt costs ₹800 with a 15% discount. What is the sale price?", ["₹680", "₹720", "₹785", "₹120"], 0, "15% of 800 = 120. Sale price = 800 − 120 = ₹680."),
    _q("Percentages", 3, "A price rises from ₹200 to ₹250. What is the percent increase?", ["20%", "25%", "50%", "5%"], 1, "Increase = 50. 50 ÷ 200 × 100 = 25%."),
    _q("Algebra", 1, "Solve: x + 7 = 15", ["6", "7", "8", "22"], 2, "Subtract 7 from both sides: x = 15 − 7 = 8."),
    _q("Algebra", 2, "Solve: 3x − 4 = 11", ["3", "5", "7", "15"], 1, "Add 4: 3x = 15. Divide by 3: x = 5."),
    _q("Algebra", 3, "Solve: 2(x + 3) = 3x − 1", ["5", "7", "−7", "1"], 1, "Expand: 2x + 6 = 3x − 1. Move terms: 7 = x."),
    _q("Geometry", 1, "Area of a rectangle 5 m long and 3 m wide?", ["8 m²", "15 m²", "16 m²", "30 m²"], 1, "Area = length × width = 5 × 3 = 15 m²."),
    _q("Geometry", 2, "Area of a triangle with base 10 cm and height 6 cm?", ["16 cm²", "30 cm²", "60 cm²", "36 cm²"], 1, "Area = ½ × base × height = ½ × 10 × 6 = 30 cm²."),
    _q("Geometry", 3, "Circumference of a circle with radius 7 cm (π = 22/7)?", ["22 cm", "44 cm", "154 cm", "14 cm"], 1, "C = 2πr = 2 × 22/7 × 7 = 44 cm."),
]
TOPICS = sorted({x["topic"] for x in QUESTIONS})
