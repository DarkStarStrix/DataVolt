import gradio as gr
import time
import os
from Nexa_Backend.Tokenization.app.Core import job_manager

STRIPE_URLS = {
    "starter": "https://buy.stripe.com/8x2dRa5JXdw67erbkNbjW01",
    "pro": "https://buy.stripe.com/aFa14o2xL63E1U73SlbjW00"
}

def run_job(plan, progress=gr.Progress()):
    user_input = {
        "plan": plan,
        "token_budget": 10000 if plan == "starter" else 50000,
        "job_type": "tokenize",
        "domain": "example"
    }
    job_id, err = job_manager.start_job(user_input)
    if err:
        return "Error: " + str(err), None, None
    last_status = ""
    while True:
        status = job_manager.get_job_status(job_id)
        if status:
            msg = status.get("status", "")
            if msg == "complete":
                url = STRIPE_URLS[plan]
                # Save the output path for download after payment
                output_path = status.get("result_path")
                # Show payment link, and only show download after payment
                return (
                    f"Dataset ready! Please [pay here]({url}) to unlock download.",
                    None,
                    output_path
                )
            elif msg == "failed":
                return f"Job failed: {status.get('error')}", None, None
            step_msg = status.get("progress", {}).get("message", "")
            if step_msg and step_msg != last_status:
                progress(step_msg)
                last_status = step_msg
        time.sleep(1)

def unlock_download(output_path):
    if output_path and os.path.exists(output_path):
        return output_path
    return None

with gr.Blocks(
    title="Nexa Data Studio",
    css="""
    body, .gradio-container {
        min-height: 100vh;
        background: #111 !important;
        color: #fff !important;
    }
    .gradio-container {
        max-width: 900px !important;
        margin: 40px auto !important;
        box-shadow: 0 2px 16px #0008;
        border-radius: 16px;
        padding: 32px 32px 24px 32px !important;
        background: #111 !important;
        color: #fff !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .footer {margin-top: 2em; color: #bbb; font-size: 0.9em; text-align: center;}
    #header {text-align: center;}
    """
) as demo:
    gr.Markdown(
        """
        <div style="display:flex;align-items:center;gap:16px;justify-content:center;">
            <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" height="40"/>
            <h1 style="margin-bottom:0;">Nexa Data Studio</h1>
        </div>
        <p style="text-align:center;">
        <b>Generate or label scientific datasets for ML research.</b>
        </p>
        """,
        elem_id="header"
    )

    gr.Markdown(
        """
        ### Choose your plan and generate your dataset. Pay only when it's ready!
        """
    )

    with gr.Row():
        starter_btn = gr.Button("Nexa Starter ($15)")
        pro_btn = gr.Button("Nexa Pro ($30)")
    status = gr.Markdown()
    download_btn = gr.Button("Unlock Download", visible=False)
    download_file = gr.File(label="Download Dataset", visible=False)

    def handle_job(plan):
        msg, _, output_path = run_job(plan)
        # Show unlock button only if dataset is ready
        if output_path:
            download_btn.visible = True
            download_btn.value = "Unlock Download"
            download_file.visible = False
        else:
            download_btn.visible = False
            download_file.visible = False
        return msg, gr.update(visible=download_btn.visible), gr.update(visible=False)

    starter_btn.click(
        fn=lambda: handle_job("starter"),
        outputs=[status, download_btn, download_file]
    )
    pro_btn.click(
        fn=lambda: handle_job("pro"),
        outputs=[status, download_btn, download_file]
    )

    def unlock_and_show_file():
        # This function is called after user clicks "Unlock Download" (assume payment done)
        # In production, verify payment before allowing download!
        # For demo, just show the file if it exists
        # The output_path should be stored in session or state for real use
        # Here, we just use the last generated file for demo
        # (You may want to improve this logic)
        files = [f for f in os.listdir("tmp") if f.endswith(".jsonl")]
        if files:
            latest = max(files, key=lambda f: os.path.getctime(os.path.join("tmp", f)))
            return gr.update(visible=True, value=os.path.join("tmp", latest))
        return gr.update(visible=False)

    download_btn.click(
        fn=unlock_and_show_file,
        outputs=download_file
    )

    gr.Markdown(
        f"""
        <div class="footer">
        &copy; {time.strftime("%Y")} Nexa Data Studio &mdash; Powered by Hugging Face Spaces<br>
        For support, contact <a href="mailto:support@nexadatastudio.com">support@nexadatastudio.com</a>
        </div>
        """
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
    print("Nexa Data Studio is running at http://localhost:7860")
