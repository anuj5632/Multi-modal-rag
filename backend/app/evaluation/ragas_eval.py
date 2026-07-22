import os

from ragas import evaluate, EvaluationDataset
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithoutReference,
    LLMContextRecall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.retrieval.retriever import retrieve_context
from app.llm.generator import generator


def _judge_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    return LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0,
        )
    )


def _judge_embeddings():
    api_key = os.getenv("GEMINI_API_KEY")
    return LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key,
        )
    )


def run_evaluation(test_cases, top_k=5):
    """
    test_cases: list of {"question": str, "ground_truth": Optional[str]}

    Runs the LIVE RAG pipeline for each question - real hybrid retrieval +
    reranking + real Gemini generation, not mocked - then scores the
    result with RAGAS.

    Metrics:
      - Faithfulness: is the answer actually supported by the retrieved
        context (i.e. did the model hallucinate)?
      - ResponseRelevancy: does the answer actually address the question?
      - LLMContextPrecisionWithoutReference: is the retrieved context
        relevant to the question (signal-to-noise of retrieval)?
      - LLMContextRecall (only if ground_truth is supplied): did
        retrieval surface everything needed to answer correctly?

    The first three are reference-free (no ground truth needed) and run
    for every question. LLMContextRecall needs a human-written reference
    answer, so it only runs for questions that include one.
    """

    judge_llm = _judge_llm()
    judge_embeddings = _judge_embeddings()

    rows = []
    any_ground_truth = any(tc.get("ground_truth") for tc in test_cases)

    for tc in test_cases:
        question = tc["question"]

        retrieved_chunks = retrieve_context(question, top_k=top_k)
        contexts = [c["text"] for c in retrieved_chunks]

        answer = generator.generate_answer(question, retrieved_chunks)

        row = {
            "user_input": question,
            "response": answer,
            "retrieved_contexts": contexts,
        }

        if any_ground_truth:
            # LLMContextRecall needs a "reference" value on every row once
            # it's included as a metric - default to empty string for
            # questions that didn't supply a ground_truth so the column
            # exists everywhere (that row just scores low/meaningless on
            # context_recall rather than crashing the whole run).
            row["reference"] = tc.get("ground_truth") or ""

        rows.append(row)

    dataset = EvaluationDataset.from_list(rows)

    has_ground_truth = any_ground_truth

    metrics = [
        Faithfulness(llm=judge_llm),
        ResponseRelevancy(llm=judge_llm, embeddings=judge_embeddings),
        LLMContextPrecisionWithoutReference(llm=judge_llm),
    ]

    if has_ground_truth:
        metrics.append(LLMContextRecall(llm=judge_llm))

    result = evaluate(dataset=dataset, metrics=metrics)

    result_df = result.to_pandas()
    metric_columns = [m.name for m in metrics]

    per_question = result_df.to_dict(orient="records")
    aggregate = {
        col: float(result_df[col].mean())
        for col in metric_columns
        if col in result_df.columns
    }

    return {
        "per_question": per_question,
        "aggregate": aggregate,
        "questions_evaluated": len(rows),
        "ground_truth_provided": has_ground_truth,
    }
