import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import sqlite3
from datetime import datetime
from fpdf import FPDF
import requests



# --- STEP 2.1: Initialize database and table ---
def init_db():
    conn = sqlite3.connect("research.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            notes TEXT NOT NULL,
            sources TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Create the database on app start ---
init_db()



# Function to export summary
def export_summary():
    topic = topic_entry.get().strip()
    notes = notes_box.get("1.0", tk.END).strip()
    sources = source_box.get("1.0", tk.END).strip()

    if not topic or not notes:
        messagebox.showwarning("Missing Info", "Topic and Notes cannot be empty.")
        return

    summary = f"🔍 Topic: {topic}\n\n📝 Notes:\n{notes}\n\n🔗 Source Links:\n{sources}"

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        initialfile=f"{topic.replace(' ', '_')}_summary.txt"
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(summary)
        messagebox.showinfo("Exported", f"Summary saved to:\n{file_path}")

def export_pdf():
    topic = topic_entry.get().strip()
    notes = notes_box.get("1.0", tk.END).strip()
    sources = source_box.get("1.0", tk.END).strip()

    if not topic or not notes:
        messagebox.showwarning("Missing Info", "Topic and Notes cannot be empty.")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Research Topic: {topic}", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Notes:\n{notes}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Sources:\n{sources}")

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF File", "*.pdf")],
        initialfile=f"{topic.replace(' ', '_')}_summary.pdf"
    )

    if file_path:
        pdf.output(file_path)
        messagebox.showinfo("Exported", f"PDF summary saved to:\n{file_path}")


def save_to_database():
    topic = topic_entry.get().strip()
    notes = notes_box.get("1.0", tk.END).strip()
    sources = source_box.get("1.0", tk.END).strip()

    if not topic or not notes:
        messagebox.showwarning("Missing Info", "Topic and Notes cannot be empty.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect("research.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO research_notes (topic, notes, sources, timestamp)
            VALUES (?, ?, ?, ?)
        """, (topic, notes, sources, timestamp))
        conn.commit()
        conn.close()

        messagebox.showinfo("Saved", "Your research has been saved to the database.")
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred:\n{e}")


def view_key_insights():
    notes = notes_box.get("1.0", tk.END).strip()
    if not notes:
        messagebox.showwarning("No Notes", "Write some notes first.")
        return

    # Extract lines starting with >> or **
    lines = notes.splitlines()
    highlights = [line for line in lines if line.strip().startswith((">>", "**"))]

    if not highlights:
        messagebox.showinfo("No Highlights", "No key insights found. Use >> or ** to mark them.")
        return

    # Display in a new window
    insight_win = tk.Toplevel(app)
    insight_win.title("🧠 Key Insights")
    insight_win.geometry("600x400")

    text_area = scrolledtext.ScrolledText(insight_win, font=("Arial", 11), wrap=tk.WORD)
    text_area.pack(padx=10, pady=10, fill='both', expand=True)

    for line in highlights:
        text_area.insert(tk.END, f"{line.strip()}\n\n")

    text_area.configure(state='disabled')

def view_saved_research():
    # Connect to DB and fetch all records
    conn = sqlite3.connect("research.db")
    cursor = conn.cursor()
    cursor.execute("SELECT topic, notes, sources, timestamp FROM research_notes ORDER BY timestamp DESC")
    results = cursor.fetchall()
    conn.close()

    if not results:
        messagebox.showinfo("No Data", "No saved research found.")
        return

    # Create a new popup window
    view_win = tk.Toplevel(app)
    view_win.title("📚 Saved Research")
    view_win.geometry("700x500")

    text_area = scrolledtext.ScrolledText(view_win, font=("Arial", 11), wrap=tk.WORD)
    text_area.pack(padx=10, pady=10, fill='both', expand=True)

    for topic, notes, sources, timestamp in results:
        entry = f"🕒 {timestamp}\n🔍 Topic: {topic}\n📝 Notes:\n{notes}\n🔗 Sources:\n{sources}\n" + "-"*60 + "\n\n"
        text_area.insert(tk.END, entry)

    text_area.configure(state='disabled')  # Make it read-only


def export_key_insights():
    notes = notes_box.get("1.0", tk.END).strip()

    if not notes:
        messagebox.showwarning("No Notes", "Write some notes first.")
        return

    # Extract key insights
    lines = notes.splitlines()
    highlights = [line.strip() for line in lines if line.strip().startswith((">>", "**"))]

    if not highlights:
        messagebox.showinfo("No Highlights", "No key insights found. Use >> or ** to mark them.")
        return

    # Ask where to save
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        initialfile="key_insights.txt"
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("🧠 Key Insights\n\n")
            f.write("\n".join(highlights))
        messagebox.showinfo("Exported", f"Key insights saved to:\n{file_path}")


def search_web_and_show(query):
    if not query.strip():
        messagebox.showwarning("Empty Search", "Please enter a search term.")
        return

    try:
        params = {
            "q": query,
            "api_key": "f57ef0648cf91221ed48ce2071e57d1a33087498aaab4cb5d2a1c57a72dec671",
            "engine": "google",
            "num": 5
        }

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        articles = data.get("organic_results", [])

        if not articles:
            messagebox.showinfo("No Results", "No articles found for this query.")
            return

        # Show results in popup window
        result_win = tk.Toplevel(app)
        result_win.title(f"🔍 Results for: {query}")
        result_win.geometry("700x500")

        canvas = tk.Canvas(result_win)
        scrollbar = tk.Scrollbar(result_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for article in articles:
            title = article.get("title", "No Title")
            snippet = article.get("snippet", "No Snippet")
            url = article.get("link", "No URL")

            # Frame per article
            article_frame = tk.Frame(scrollable_frame, bd=1, relief="groove", padx=8, pady=6)
            article_frame.pack(fill='x', padx=10, pady=5)

            tk.Label(article_frame, text=title, font=("Arial", 11, "bold"), wraplength=600, justify='left').pack(anchor='w')
            tk.Label(article_frame, text=snippet, font=("Arial", 10), wraplength=600, justify='left', fg="gray").pack(anchor='w', pady=(2, 4))
            tk.Label(article_frame, text=url, font=("Arial", 9, "underline"), fg="blue", cursor="hand2", wraplength=600, justify='left').pack(anchor='w')

            # Add to sources button
            def add_link(u=url):
                current = source_box.get("1.0", tk.END).strip()
                new_text = current + ("\n" if current else "") + u
                source_box.delete("1.0", tk.END)
                source_box.insert(tk.END, new_text)

            tk.Button(article_frame, text="➕ Add to Source Links", command=add_link, bg="#4CAF50", fg="white").pack(anchor='e', pady=(5, 0))

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


# --- Create the main app window ---
app = tk.Tk()
app.title("Focused Research Assistant")
app.geometry("950x700")
app.configure(bg="#F3F4F6")  # Soft background color

# === TOP SECTION: Topic + Web Search ===
top_frame = tk.Frame(app, bg="#F3F4F6", pady=10)
top_frame.pack(fill='x')

tk.Label(top_frame, text="📝 Topic:", font=("Arial", 12, "bold"), bg="#F3F4F6").grid(row=0, column=0, sticky='w', padx=10)
topic_entry = tk.Entry(top_frame, font=("Arial", 12), width=60)
topic_entry.grid(row=0, column=1, padx=5)

tk.Label(top_frame, text="🌐 Web Search:", font=("Arial", 12, "bold"), bg="#F3F4F6").grid(row=1, column=0, sticky='w', padx=10, pady=(10, 0))
web_search_entry = tk.Entry(top_frame, font=("Arial", 12), width=60)
web_search_entry.grid(row=1, column=1, padx=5, pady=(10, 0))

search_button = tk.Button(top_frame, text="🔍 Search", font=("Arial", 11, "bold"),
                          bg="#3B82F6", fg="white", command=lambda: search_web_and_show(web_search_entry.get()))
search_button.grid(row=1, column=2, padx=10)

# === MIDDLE SECTION: Notes + Sources ===
middle_frame = tk.Frame(app, bg="#F3F4F6", pady=10)
middle_frame.pack(fill='both', expand=True)

tk.Label(middle_frame, text="🗒️ Notes:", font=("Arial", 12, "bold"), bg="#F3F4F6").grid(row=0, column=0, sticky='nw', padx=10)
notes_box = scrolledtext.ScrolledText(middle_frame, font=("Arial", 11), width=50, height=20)
notes_box.grid(row=1, column=0, padx=10, pady=5)

tk.Label(middle_frame, text="🔗 Sources:", font=("Arial", 12, "bold"), bg="#F3F4F6").grid(row=0, column=1, sticky='nw', padx=10)
source_box = scrolledtext.ScrolledText(middle_frame, font=("Arial", 11), width=40, height=20)
source_box.grid(row=1, column=1, padx=10, pady=5)

# === BOTTOM SECTION: Action Buttons ===
bottom_frame = tk.Frame(app, bg="#F3F4F6", pady=10)
bottom_frame.pack()

button_configs = [
    ("📤 Export Summary", "#4CAF50", export_summary),
    ("📄 Export PDF", "#795548", export_pdf),
    ("💾 Save to DB", "#2196F3", save_to_database),
    ("📚 View Saved", "#FF9800", view_saved_research),
    ("🧠 Key Insights", "#9C27B0", view_key_insights),
    ("📤 Export Insights", "#3F51B5", export_key_insights),
]

for label, color, func in button_configs:
    btn = tk.Button(bottom_frame, text=label, font=("Arial", 11, "bold"), bg=color, fg="white", width=18, command=func)
    btn.pack(side='left', padx=8, pady=5)

# Start the application
app.mainloop()
