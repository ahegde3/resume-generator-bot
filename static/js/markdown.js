// Simple markdown renderer for chat messages
const markdownRenderer = {
  // Convert markdown to HTML
  render: function (text) {
    if (!text) return "";

    // Process code blocks
    text = this.processCodeBlocks(text);

    // Process headers
    text = text.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    text = text.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    text = text.replace(/^# (.*$)/gim, "<h1>$1</h1>");

    // Process lists
    text = text.replace(/^\s*\n\* (.*$)/gim, "<ul>\n<li>$1</li>\n</ul>");
    text = text.replace(/^\s*\n- (.*$)/gim, "<ul>\n<li>$1</li>\n</ul>");
    text = text.replace(/^\s*\n\d+\. (.*$)/gim, "<ol>\n<li>$1</li>\n</ol>");

    // Process consecutive list items
    text = text.replace(/<\/ul>\s*<ul>/g, "");
    text = text.replace(/<\/ol>\s*<ol>/g, "");

    // Process emphasis (bold, italic)
    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
    text = text.replace(/\_\_(.*?)\_\_/g, "<strong>$1</strong>");
    text = text.replace(/\_(.*?)\_/g, "<em>$1</em>");

    // Process links
    text = text.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    // Process paragraphs
    text = text.replace(/^\s*(\n)?(.+)/gim, function (m) {
      return /\<(\/)?(h|ul|ol|li|blockquote|pre|img)/.test(m)
        ? m
        : "<p>" + m + "</p>";
    });

    // Remove empty paragraphs
    text = text.replace(/<p><\/p>/g, "");

    return text;
  },

  // Process code blocks with syntax highlighting
  processCodeBlocks: function (text) {
    // Replace ```language\ncode``` with <pre><code class="language">code</code></pre>
    return text.replace(
      /```(.*?)\n([\s\S]*?)```/g,
      function (match, language, code) {
        return (
          '<pre><code class="language-' +
          language +
          '">' +
          this.escapeHtml(code) +
          "</code></pre>"
        );
      }.bind(this)
    );
  },

  // Escape HTML special characters
  escapeHtml: function (text) {
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return text.replace(/[&<>"']/g, function (m) {
      return map[m];
    });
  },
};
