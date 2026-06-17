import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { Tag } from '../../../services/tag.service';

interface ParsedSection {
  type: 'title' | 'description' | 'examples' | 'constraints' | 'generic';
  content: string;
  examples?: Array<{
    input?: string | SafeHtml;
    output?: string;
    explanation?: string | SafeHtml;
  }>;
  constraints?: string[];
}

@Component({
  selector: 'app-description',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './description.component.html',
  styleUrl: './description.component.scss'
})
export class DescriptionComponent implements OnChanges {
  @Input() content: string = '';
  @Input() isCompleted: boolean = false;
  @Input() questionTags: Tag[] = [];
  parsedSections: ParsedSection[] = [];

  constructor(private sanitizer: DomSanitizer) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['content'] && this.content) {
      this.parsedSections = this.parseContent(this.content);
    }
  }

  // Bypass sanitization for HTML that contains inline styles.
  // Content comes from static JSON files in the codebase, not user input.
  private trust(html: string): string | SafeHtml {
    return html.includes('style=')
      ? this.sanitizer.bypassSecurityTrustHtml(html)
      : html;
  }

  private parseContent(html: string): ParsedSection[] {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const sections: ParsedSection[] = [];

    // Extract title (h2)
    const h2 = doc.querySelector('h2');
    if (h2) {
      sections.push({
        type: 'title',
        content: h2.textContent || ''
      });
    }

    // Extract main description (paragraphs before Examples or Constraints)
    const descriptionParts: string[] = [];
    let currentNode = h2?.nextSibling;

    while (currentNode) {
      if (currentNode.nodeType === Node.ELEMENT_NODE) {
        const el = currentNode as Element;
        const text = el.textContent?.toLowerCase() || '';

        // Stop if we hit Examples or Constraints heading
        if (el.tagName === 'H3' && (text.includes('example') || text.includes('constraint'))) {
          break;
        }

        // Collect description content
        if (['P', 'UL', 'OL', 'PRE', 'BLOCKQUOTE', 'TABLE'].includes(el.tagName)) {
          descriptionParts.push(el.outerHTML);
        }
      }
      currentNode = currentNode.nextSibling;
    }

    if (descriptionParts.length > 0) {
      sections.push({
        type: 'description',
        content: descriptionParts.join('')
      });
    }

    // Extract Examples
    const examplesSection = this.extractExamples(doc);
    if (examplesSection) {
      sections.push(examplesSection);
    }

    // Extract Constraints
    const constraintsSection = this.extractConstraints(doc);
    if (constraintsSection) {
      sections.push(constraintsSection);
    }

    return sections;
  }

  private extractExamples(doc: Document): ParsedSection | null {
    const headings = Array.from(doc.querySelectorAll('h3'));
    const examplesHeading = headings.find(h => h.textContent?.toLowerCase().includes('example'));

    if (!examplesHeading) return null;

    // Find the list following the Examples heading
    let listElement = examplesHeading.nextElementSibling;
    while (listElement && listElement.tagName !== 'UL') {
      listElement = listElement.nextElementSibling;
    }

    if (!listElement) return null;

    const examples: Array<{ input?: string | SafeHtml; output?: string; explanation?: string | SafeHtml }> = [];
    const items = Array.from(listElement.querySelectorAll('li'));

    items.forEach(item => {
      const text = item.innerHTML;
      const example: { input?: string | SafeHtml; output?: string; explanation?: string | SafeHtml } = {};

      // Try to extract with <strong> tags first (newer format)
      // Only stop at <br> when followed by Output (allows multi-line inputs)
      let inputMatch = text.match(/<strong>Input:<\/strong>\s*(.*?)(?=<br\s*\/?>\s*<strong>Output|<strong>Output|<\/li>|$)/is);
      if (inputMatch) {
        let inputText = inputMatch[1].trim();
        inputText = inputText.replace(/<\/?code>/gi, '');
        inputText = inputText.replace(/<br\s*\/?>/gi, '\n'); // Convert <br> to newlines
        inputText = inputText.replace(/<(?!\/?span\b)[^>]+>/gi, ''); // Remove non-span HTML tags
        example.input = this.trust(inputText.trim());
      } else {
        // Try plain text format (older format): "Input: ... <br>"
        inputMatch = text.match(/Input:\s*(.*?)(?=<br\s*\/?>\s*Output:|Output:|$)/is);
        if (inputMatch) {
          let inputText = inputMatch[1].trim();
          inputText = inputText.replace(/<\/?code>/gi, '');
          inputText = inputText.replace(/<br\s*\/?>/gi, '\n'); // Convert <br> to newlines
          inputText = inputText.replace(/<(?!\/?span\b)[^>]+>/gi, ''); // Remove non-span HTML tags
          example.input = this.trust(inputText.trim());
        }
      }

      // Try to extract Output with <strong> tags first
      // Only stop at <br> when followed by Explanation (allows multi-line outputs)
      let outputMatch = text.match(/<strong>Output:<\/strong>\s*(.*?)(?=<br\s*\/?>\s*<strong>Explanation|<strong>Explanation|<\/li>|$)/is);
      if (outputMatch) {
        let outputText = outputMatch[1].trim();
        outputText = outputText.replace(/<\/?code>/gi, '');
        outputText = outputText.replace(/<br\s*\/?>/gi, '\n'); // Convert <br> to newlines
        outputText = outputText.replace(/<(?!\/?span\b)[^>]+>/gi, ''); // Remove non-span HTML tags
        example.output = outputText.trim();
      } else {
        // Try plain text format
        outputMatch = text.match(/Output:\s*(.*?)(?=<br\s*\/?>\s*Explanation:|Explanation:|$)/is);
        if (outputMatch) {
          let outputText = outputMatch[1].trim();
          outputText = outputText.replace(/<\/?code>/gi, '');
          outputText = outputText.replace(/<br\s*\/?>/gi, '\n'); // Convert <br> to newlines
          outputText = outputText.replace(/<(?!\/?span\b)[^>]+>/gi, ''); // Remove non-span HTML tags
          example.output = outputText.trim();
        }
      }

      // Extract Explanation (both formats)
      let explanationMatch = text.match(/<strong>Explanation:<\/strong>\s*(.*?)(?=<\/li>|$)/is);
      if (explanationMatch) {
        example.explanation = this.trust(explanationMatch[1].trim());
      } else {
        explanationMatch = text.match(/Explanation:\s*(.*?)(?=<\/li>|$)/is);
        if (explanationMatch) {
          example.explanation = this.trust(explanationMatch[1].trim());
        }
      }

      // Only add if we have at least input or output
      if (example.input || example.output) {
        examples.push(example);
      }
    });

    return {
      type: 'examples',
      content: '',
      examples
    };
  }

  private extractConstraints(doc: Document): ParsedSection | null {
    const headings = Array.from(doc.querySelectorAll('h3'));
    const constraintsHeading = headings.find(h => h.textContent?.toLowerCase().includes('constraint'));

    if (!constraintsHeading) return null;

    let listElement = constraintsHeading.nextElementSibling;
    while (listElement && listElement.tagName !== 'UL') {
      listElement = listElement.nextElementSibling;
    }

    if (!listElement) return null;

    const constraints: string[] = [];
    const items = Array.from(listElement.querySelectorAll('li'));

    items.forEach(item => {
      constraints.push(item.innerHTML.trim());
    });

    return {
      type: 'constraints',
      content: '',
      constraints
    };
  }
}
