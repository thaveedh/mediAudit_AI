from rag import ask

while True:
    question = input("\nAsk a medical question (type 'exit' to quit): ")

    if question.lower() == "exit":
        break

    answer = ask(question)

    print("\n" + "=" * 60)
    print("AI RESPONSE")
    print("=" * 60)
    print(answer)