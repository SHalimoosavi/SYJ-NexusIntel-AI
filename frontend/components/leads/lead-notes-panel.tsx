"use client";

import { useEffect, useState } from "react";
import { createLeadNote, getLeadNotes, type LeadNote } from "@/lib/api";

type Props = {
  leadId: number;
};

export default function LeadNotesPanel({ leadId }: Props) {
  const [notes, setNotes] = useState<LeadNote[]>([]);
  const [newNote, setNewNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    getLeadNotes(leadId)
      .then((data) => {
        if (active) setNotes(data);
      })
      .catch((loadError: unknown) => {
        if (active) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Failed to load notes"
          );
        }
      });

    return () => {
      active = false;
    };
  }, [leadId]);

  async function addNote() {
    const noteText = newNote.trim();
    if (!noteText || saving) return;

    setSaving(true);
    setError("");
    try {
      await createLeadNote(leadId, noteText);
      setNewNote("");
      setNotes(await getLeadNotes(leadId));
    } catch (saveError: unknown) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Failed to save note"
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="glass rounded-3xl p-6">
      <h2 className="text-2xl font-black mb-4">Sales Journal</h2>

      <textarea
        value={newNote}
        onChange={(event) => setNewNote(event.target.value)}
        placeholder="Add sales note..."
        maxLength={10000}
        className="w-full rounded-xl bg-black/20 p-3 mb-4"
      />

      {error && (
        <p role="alert" className="text-sm text-red-400 mb-3">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={addNote}
        disabled={saving || !newNote.trim()}
        className="px-4 py-2 rounded-xl bg-cyan-600 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save Note"}
      </button>

      <div className="mt-6 space-y-3">
        {notes.map((note) => (
          <div
            key={note.id}
            className="rounded-xl bg-black/20 p-3"
          >
            <p>{note.note}</p>
            <p className="text-xs text-slate-400 mt-2">
              {new Date(note.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
