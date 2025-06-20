"""
Core.py: Orchestrates dataset generation jobs, plan enforcement, and background processing.
"""
import threading
import uuid
import os
import json
from .Config import PLAN_LIMITS, tmp_dir
from .Progress import progress_tracker
from .Payment import payment_manager

# Import your tokenizer module here (example)
import nltk

class JobManager:
    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()

    def start_job(self, user_input):
        plan = user_input.get("plan")
        token_budget = user_input.get("token_budget")
        job_type = user_input.get("job_type", "tokenize")  # "tokenize", "corpus", or "label"
        # For label jobs, token_budget is determined after upload
        if job_type != "label" and not payment_manager.check_plan_limit(plan, token_budget):
            return None, "Plan limit exceeded"
        job_id = str(uuid.uuid4())
        with self.lock:
            self.jobs[job_id] = {
                "status": "pending",
                "plan": plan,
                "token_budget": token_budget,
                "job_type": job_type,
                "user_input": user_input
            }
        if job_type == "corpus":
            thread = threading.Thread(target=self._run_corpus_pipeline, args=(job_id,))
        elif job_type == "label":
            thread = threading.Thread(target=self._run_label_pipeline, args=(job_id,))
        else:
            thread = threading.Thread(target=self._run_job, args=(job_id, user_input))
        thread.start()
        return job_id, None

    def _run_job(self, job_id, user_input):
        try:
            progress_tracker.start_job(job_id, total_steps=6)
            # Step 1: Data retrieval
            progress_tracker.update(job_id, 1, "Retrieving data from sources...")
            domain = user_input.get("domain")
            token_budget = user_input.get("token_budget")
            plan = user_input.get("plan")
            custom_seed = user_input.get("custom_seed", None)
            # Step 2: Preprocessing
            progress_tracker.update(job_id, 2, "Preprocessing and cleaning data...")
            # Step 3: Tokenization & Labeling
            progress_tracker.update(job_id, 3, "Tokenizing and labeling samples...")
            # Step 4: Validation & Stats
            progress_tracker.update(job_id, 4, "Validating and computing statistics...")
            # Step 5: Formatting output
            progress_tracker.update(job_id, 5, "Formatting dataset as JSONL...")
            # Call tokenizer pipeline (implement in tokenization/tokenizer.py)
            result = generate_dataset(
                domain=domain,
                token_budget=token_budget,
                plan=plan,
                custom_seed=custom_seed,
                progress_callback=lambda step, msg: progress_tracker.update(job_id, step, msg)
            )
            # Step 6: Save output
            os.makedirs(tmp_dir, exist_ok=True)
            output_path = os.path.join(tmp_dir, f"{domain}_{token_budget}_tokens_{job_id}.jsonl")
            with open(output_path, "w", encoding="utf-8") as f:
                for line in result["jsonl_lines"]:
                    f.write(line + "\n")
            progress_tracker.update(job_id, 6, "Dataset ready for download.")
            progress_tracker.complete(job_id)
            with self.lock:
                self.jobs[job_id]["status"] = "complete"
                self.jobs[job_id]["result_path"] = output_path
                self.jobs[job_id]["stats"] = result.get("stats", {})
        except Exception as e:
            progress_tracker.update(job_id, 0, f"Job failed: {str(e)}")
            with self.lock:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error"] = str(e)

    def _run_corpus_pipeline(self, job_id):
        try:
            with self.lock:
                user_input = self.jobs[job_id]["user_input"]
            plan = user_input.get("plan")
            token_budget = user_input.get("token_budget")
            progress_tracker.start_job(job_id, total_steps=5)
            progress_tracker.update(job_id, 1, "Building scientific corpus...")
            config = CorpusConfig()
            builder = ScientificCorpusBuilder(config)
            corpus, stats = builder.build_corpus_scoped(plan, token_budget)
            progress_tracker.update(job_id, 2, "Formatting dataset as JSONL...")
            jsonl_lines = [json.dumps(paper, ensure_ascii=False) for paper in corpus]
            progress_tracker.update(job_id, 3, "Finalizing output...")
            progress_tracker.update(job_id, 4, "Corpus ready for download.")
            progress_tracker.complete(job_id)
            with self.lock:
                self.jobs[job_id]["status"] = "complete"
                self.jobs[job_id]["jsonl_lines"] = jsonl_lines
                self.jobs[job_id]["stats"] = stats
                self.jobs[job_id]["actual_tokens"] = stats.get("total_tokens", 0)
        except Exception as e:
            progress_tracker.update(job_id, 0, f"Job failed: {str(e)}")
            with self.lock:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error"] = str(e)

    def _run_label_pipeline(self, job_id):
        try:
            with self.lock:
                user_input = self.jobs[job_id]["user_input"]
                plan = self.jobs[job_id]["plan"]
            progress_tracker.start_job(job_id, total_steps=4)
            progress_tracker.update(job_id, 1, "Loading and preprocessing dataset...")
            dataset_text = user_input.get("dataset_text", "")
            if not dataset_text:
                raise ValueError("No dataset text provided.")
            tokens = nltk.word_tokenize(dataset_text)
            num_tokens = len(tokens)
            with self.lock:
                self.jobs[job_id]["actual_tokens"] = num_tokens
            if not payment_manager.check_plan_limit(plan, num_tokens):
                raise ValueError("Plan limit exceeded.")
            progress_tracker.update(job_id, 2, "Tokenizing and labeling dataset...")
            preprocessor = QLoRAPreprocessor()
            labeled_data = preprocessor.preprocess_function(dataset_text)
            jsonl_lines = [json.dumps({"text": item}, ensure_ascii=False) for item in labeled_data]
            stats = {"token_count": num_tokens, "sample_count": len(labeled_data)}
            progress_tracker.update(job_id, 3, "Dataset ready for download.")
            progress_tracker.complete(job_id)
            with self.lock:
                self.jobs[job_id]["status"] = "complete"
                self.jobs[job_id]["jsonl_lines"] = jsonl_lines
                self.jobs[job_id]["stats"] = stats
        except Exception as e:
            progress_tracker.update(job_id, 0, f"Job failed: {str(e)}")
            with self.lock:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error"] = str(e)

    def get_job_status(self, job_id):
        with self.lock:
            return self.jobs.get(job_id, None)

job_manager = JobManager()
