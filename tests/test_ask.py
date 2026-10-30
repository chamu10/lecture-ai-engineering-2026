from types import SimpleNamespace

from app import ask


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
        text="テスト回答",
    )
    client = SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **kwargs: response)
    )
    monkeypatch.setattr(ask.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")

    result = ask.ask("テスト質問")

    assert result == "テスト回答"
    assert capsys.readouterr().out == "[usage] input: 12 tokens, output: 7 tokens\n"


def test_interactive_chat_sends_followups_in_the_same_chat(monkeypatch, capsys):
    sent_messages = []

    def send_message(message):
        sent_messages.append(message)
        return SimpleNamespace(
            usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
            text=f"回答: {message}",
        )

    chat = SimpleNamespace(send_message=send_message)
    client = SimpleNamespace(chats=SimpleNamespace(create=lambda **kwargs: chat))
    monkeypatch.setattr(ask.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    questions = iter(["LoRAとは？", "もう少し簡単に", "quit"])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))

    ask.interactive_chat()

    assert sent_messages == ["LoRAとは？", "もう少し簡単に"]
    output = capsys.readouterr().out
    assert "回答: LoRAとは？" in output
    assert "回答: もう少し簡単に" in output
    assert output.count("[usage] input: 12 tokens, output: 7 tokens") == 2