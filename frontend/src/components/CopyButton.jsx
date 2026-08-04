import { useEffect, useRef, useState } from "react";

export default function CopyButton({ value, label = "Copy" }) {
  const [copied, setCopied] = useState(false);
  const [copyFailed, setCopyFailed] = useState(false);

  const timeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  function copyWithFallback(text) {
    const textArea = document.createElement("textarea");

    textArea.value = text;
    textArea.setAttribute("readonly", "");

    textArea.style.position = "fixed";
    textArea.style.top = "0";
    textArea.style.left = "-9999px";
    textArea.style.opacity = "0";

    document.body.appendChild(textArea);

    textArea.focus();
    textArea.select();

    const copiedSuccessfully = document.execCommand("copy");

    document.body.removeChild(textArea);

    if (!copiedSuccessfully) {
      throw new Error("Copy command failed.");
    }
  }

  async function handleCopy() {
    try {
      setCopyFailed(false);

      if (window.isSecureContext && navigator.clipboard) {
        await navigator.clipboard.writeText(value);
      } else {
        copyWithFallback(value);
      }

      setCopied(true);

      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = window.setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      console.error("Unable to copy booking reference:", error);

      setCopied(false);
      setCopyFailed(true);

      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = window.setTimeout(() => {
        setCopyFailed(false);
      }, 2500);
    }
  }

  return (
    <button
      type="button"
      className="copy-button"
      onClick={handleCopy}
      disabled={!value}
    >
      {copied ? "Copied ✓" : copyFailed ? "Copy failed" : label}
    </button>
  );
}
