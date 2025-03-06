from g4f.client import Client
def clear_screen(master):
    """Clears all widgets from the given master widget."""
    for widget in master.winfo_children():
        widget.destroy()

# content analysis/report calling function
def report_generation(prompt):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Capture the response text and split into keywords
    #print(prompt)
    result = response.choices[0].message.content
    return result