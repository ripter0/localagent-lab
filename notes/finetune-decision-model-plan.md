Thank you for the clarification. Now I understand the **rizzo-flow** model architecture completely. It's a
**structured decision-routing model** that outputs probabilities/scores for predefined options, not a general text
generator.

---

## 🎯 Finetuning Goal for CleanSignal

You want to finetune the **decision model** (spark-x2.5-4b-rizzo-flow-lora-q8_0.gguf) for **CleanSignal-specific
routing tasks**, while keeping the **coding agent** (qwen3.5-9b) separate for code generation.

---

## 📋 Finetuning Plan (What Would Be Needed)

### 1. Training Script Structure
You would need a **Python script** (`train_decision.py`) that does the following:

*   **Import Libraries:** It would need to load AI training libraries (Transformers, PEFT, Accelerate, Datasets,
BitsAndBytes)
*   **Load Base Model:** It would load the base Spark 2.5B model weights (unquantized) from your Ollama weights
*   **Load LoRA Config:** It would load the existing LoRA configuration from your current GGUF adapter
*   **Load Dataset:** It would read your JSONL file with the `state → questions → answers` schema
*   **Configure Training:** It would set LoRA hyperparameters (rank, alpha, dropout, learning rate)
*   **Run Training Loop:** It would execute training using a framework like `trl` or `peft`
*   **Save Finetuned Model:** It would save the new LoRA adapter weights to a new GGUF file

### 2. Dataset Requirements
You would need a **JSONL file** (`clean_signal_training.jsonl`) with examples matching your schema:

```jsonl
{
  "state": "Senior backend engineer, 8 years...",
  "model": "rizzo-latest",
  "questions": {
    "python": {"type": "noul", "instructions": "Does the candidate have strong Python experience?"},
    "lead": {"type": "noul", "instructions": "Has the candidate managed or led other engineers?"},
    ...
  }
}
```

**For CleanSignal, you would need examples like:**
- Pollution report classification (type, department, severity)
- Synthetic cases matching your routing logic
- Historical cases with labeled decisions

### 3. Training Hardware
*   **GPU:** At least 6GB-8GB VRAM (for 4B model + batch size)
*   **RAM:** 16GB+ system RAM
*   **Storage:** 10GB+ for model weights and training logs

### 4. Training Configuration
*   **LoRA Rank:** 16-64 (for decision tasks)
*   **Learning Rate:** 1e-4 to 1e-3 (small model, low rate)
*   **Epochs:** 3-5 (avoid overfitting)
*   **Batch Size:** 2-4 (memory constrained)

### 5. Evaluation Script
You would need a **separate Python script** (`evaluate_decision.py`) that:
*   Loads the finetuned model
*   Tests on validation dataset
*   Outputs accuracy/confusion matrix for routing decisions
*   Saves metrics to a log file

### 6. Integration with Agent
After finetuning:
*   You would need to **update your agent.py** to load the new GGUF file
*   You would need to **verify the model outputs valid JSON** for your decision tasks
*   You would need to **test the model** with CleanSignal-specific routing queries

### 7. Alternative: Prompt-Based Finetuning
If full finetuning is too resource-intensive, you could consider:
*   **Prompt Engineering:** Add CleanSignal examples to the system prompt
*   **Few-Shot Learning:** Add routing examples to the input state
*   **External API:** Use a separate classification service for routing

---

## ❓ Questions I Need to Answer

Before proceeding, I need to clarify:

1. **Training Framework:** Do you prefer to use `trl`, `peft`, or `llama.cpp` training tools?
2. **Dataset Availability:** Do you have historical pollution reports with labels, or do you need to generate
synthetic data?
3. **GPU Hardware:** What GPU do you have available? (This affects batch size and training time)
4. **Integration Method:** Do you want to use the finetuned model directly in Ollama, or load it via
llama-cpp-python in your agent?
5. **Evaluation Criteria:** What metrics matter most? (Accuracy, confidence scores, latency)

---

## 🔄 Next Steps

Based on your answers, I can provide:
1. **Training script structure** (without writing code)
2. **Dataset format specification** (JSONL schema)
3. **Evaluation metrics** (what to measure)
4. **Integration instructions** (how to load the new model)

Would you like to proceed with preparing the training dataset, or would you prefer to explore prompt-based
alternatives first?