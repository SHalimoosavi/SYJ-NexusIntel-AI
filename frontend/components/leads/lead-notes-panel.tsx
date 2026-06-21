"use client";

import { useEffect, useState } from "react";

const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

type Note = {
  id: number;
  lead_id: number;
  note: string;
  created_at: string;
};

type Props = {
  leadId: number;
};

export default function LeadNotesPanel({
  leadId,
}: Props) {
  const [notes, setNotes] = useState<
    Note[]
  >([]);

  const [newNote, setNewNote] =
    useState("");

  async function loadNotes() {
    try {
      const response =
        await fetch(
          `${API_BASE}/lead-notes/${leadId}`
        );

      const data =
        await response.json();

      setNotes(data);
    } catch (error) {
      console.error(error);
    }
  }

  async function addNote() {
    if (!newNote.trim()) {
      return;
    }

    try {
      await fetch(
        `${API_BASE}/lead-notes`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            lead_id: leadId,
            note: newNote,
          }),
        }
      );

      setNewNote("");

      loadNotes();
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    loadNotes();
  }, [leadId]);

  return (
    <div className="glass rounded-3xl p-6">
      <h2 className="text-2xl font-black mb-4">
        Sales Journal
      </h2>

      <textarea
        value={newNote}
        onChange={(e) =>
          setNewNote(
            e.target.value
          )
        }
        placeholder="Add sales note..."
        className="w-full rounded-xl bg-black/20 p-3 mb-4"
      />

      <button
        onClick={addNote}
        className="px-4 py-2 rounded-xl bg-cyan-600"
      >
        Save Note
      </button>

      <div className="mt-6 space-y-3">
        {notes.map((note) => (
          <div
            key={note.id}
            className="rounded-xl bg-black/20 p-3"
          >
            <p>{note.note}</p>

            <p className="text-xs text-slate-400 mt-2">
              {new Date(
                note.created_at
              ).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
