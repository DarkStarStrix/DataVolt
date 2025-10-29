import pandas as pd

def generate_report(input_csv, output_txt):
    df = pd.read_csv(input_csv)
    positive_posts = df[df['label'] == 1]
    negative_posts = df[df['label'] == 0]

    with open(output_txt, 'w') as f:
        f.write("Report on Data Engineering Posts\n")
        f.write("===============================\n\n")
        f.write(f"Total Posts: {len(df)}\n")
        f.write(f"Positive Posts: {len(positive_posts)}\n")
        f.write(f"Negative Posts: {len(negative_posts)}\n\n")
        f.write("Sample Positive Post:\n")
        f.write(positive_posts.iloc[0]['text'] + "\n\n")
        f.write("Sample Negative Post:\n")
        f.write(negative_posts.iloc[0]['text'] + "\n")

if __name__ == "__main__":
    generate_report('preprocessed_data.csv', 'report.txt')
