# ai_mentor.py

PREDEFINED_QUESTIONS = {
    "What are the key principles of sustainable urban design?": {
        "answer": "Sustainable urban design focuses on creating environmentally friendly, socially equitable, and economically viable cities. Key principles include promoting mixed-use development, prioritizing walkability and public transit, integrating green spaces (like parks and green roofs), managing resources like water and energy efficiently, and designing resilient infrastructure to handle climate change impacts.",
        "topic": "Sustainability"
    },
    "How can we improve public transit accessibility?": {
        "answer": "Improving public transit involves a multi-faceted approach: expanding service to underserved areas, increasing frequency and reliability of buses and trains, ensuring stations are safe and accessible for people with disabilities (e.g., with ramps and elevators), integrating payment systems, and creating dedicated bus lanes to reduce travel time. Combining transit hubs with affordable housing and local services also boosts accessibility.",
        "topic": "Transit"
    },
    "What is 'Green Space Equity' and why is it important?": {
        "answer": "Green Space Equity refers to the fair distribution of parks, gardens, and other green areas across all neighborhoods, regardless of income or demographics. It's crucial because green spaces improve mental and physical health, reduce the urban heat island effect, improve air quality, and provide community gathering spots. Inequitable distribution can lead to significant health and social disparities between neighborhoods.",
        "topic": "Equity"
    },
    "What are effective strategies for reducing urban heat island effect?": {
        "answer": "To combat the urban heat island effect, cities can implement several strategies. These include planting more trees to provide shade, installing 'cool roofs' with reflective materials, creating green roofs, and using permeable pavements that absorb less heat. Increasing the number of parks and water features also helps cool the urban environment.",
        "topic": "Environment"
    },
    "How can zoning laws be updated to promote mixed-use development?": {
        "answer": "Zoning reform is key to enabling mixed-use neighborhoods. Strategies include creating new zoning categories that explicitly permit a combination of residential, commercial, and light industrial uses in the same building or area. Reducing or eliminating minimum parking requirements, allowing for higher density development near transit hubs, and streamlining the approval process for mixed-use projects are also effective measures.",
        "topic": "Zoning"
    }
}

def get_predefined_questions():
    """Returns the list of predefined questions."""
    return list(PREDEFINED_QUESTIONS.keys())

def get_answer(question):
    """
    Retrieves an answer for a given question from the predefined knowledge base.
    """
    return PREDEFINED_QUESTIONS.get(question, {
        "answer": "I'm sorry, I don't have an answer for that question right now. Please select from one of the predefined questions or consult a specialized urban planning resource.",
        "topic": "General"
    })

if __name__ == '__main__':
    # Example usage
    questions = get_predefined_questions()
    print("--- Predefined Questions ---")
    for q in questions:
        print(f"- {q}")

    print("\n--- Sample Answer ---")
    sample_q = questions[0]
    answer_data = get_answer(sample_q)
    print(f"Q: {sample_q}")
    print(f"A: {answer_data['answer']}")
