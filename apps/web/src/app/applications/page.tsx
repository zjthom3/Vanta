"use client";

import { DragDropContext, Draggable, Droppable, type DropResult } from "@hello-pangea/dnd";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { format } from "date-fns";
import { useEffect, useMemo, useState } from "react";
import { useSession } from "next-auth/react";

import { getJson, patchJson, postFormData } from "@/lib/api-client";

type StageKey = "prospect" | "applied" | "screen" | "interview" | "offer" | "rejected" | "accepted";

const STAGES: Array<{ key: StageKey; label: string }> = [
  { key: "prospect", label: "Prospect" },
  { key: "applied", label: "Applied" },
  { key: "screen", label: "Screen" },
  { key: "interview", label: "Interview" },
  { key: "offer", label: "Offer" },
  { key: "rejected", label: "Rejected" },
  { key: "accepted", label: "Accepted" },
];

type TaskItem = {
  id: string;
  title: string;
  type?: string | null;
  due_at?: string | null;
  completed_at?: string | null;
};

type ApplicationItem = {
  id: string;
  title: string;
  company: string | null;
  stage: StageKey;
  url: string | null;
  notes_count: number;
  tasks: TaskItem[];
};

type NoteItem = {
  id: string;
  body: string | null;
  attachment_url: string | null;
  attachment_name: string | null;
  attachment_content_type: string | null;
  created_at: string;
};

type ApplicationsResponse = ApplicationItem[];

type NotesResponse = NoteItem[];

const emptyBoard = (): Record<StageKey, ApplicationItem[]> =>
  STAGES.reduce(
    (acc, stage) => {
      acc[stage.key] = [];
      return acc;
    },
    {} as Record<StageKey, ApplicationItem[]>,
  );

export default function ApplicationsPage() {
  const queryClient = useQueryClient();
  const { data: session } = useSession();
  const userId = session?.user?.id;
  const [board, setBoard] = useState<Record<StageKey, ApplicationItem[]>>(emptyBoard);
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);
  const [noteBody, setNoteBody] = useState("");
  const [noteFile, setNoteFile] = useState<File | null>(null);

  const applicationsQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["applications", userId],
    queryFn: async () => getJson<ApplicationsResponse>("/applications/", { userId }),
  });

  useEffect(() => {
    if (!applicationsQuery.data) {
      setBoard(emptyBoard());
      return;
    }
    const grouped = emptyBoard();
    for (const application of applicationsQuery.data) {
      grouped[application.stage]?.push(application);
    }
    setBoard(grouped);
  }, [applicationsQuery.data]);

  const stageMutation = useMutation({
    mutationFn: async (variables: { id: string; stage: StageKey }) =>
      patchJson(`/applications/${variables.id}`, { stage: variables.stage }, { userId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications", userId] });
    },
  });

  const notesQuery = useQuery({
    enabled: Boolean(userId && selectedApplicationId),
    queryKey: ["application-notes", selectedApplicationId, userId],
    queryFn: async () =>
      getJson<NotesResponse>(`/applications/${selectedApplicationId}/notes`, { userId }),
  });

  const addNoteMutation = useMutation({
    mutationFn: async (variables: { applicationId: string; formData: FormData }) =>
      postFormData<NoteItem>(`/applications/${variables.applicationId}/notes`, variables.formData, { userId }),
    onSuccess: () => {
      setNoteBody("");
      setNoteFile(null);
      notesQuery.refetch();
      queryClient.invalidateQueries({ queryKey: ["applications", userId] });
    },
  });

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) {
      return;
    }
    const sourceStage = result.source.droppableId as StageKey;
    const destinationStage = result.destination.droppableId as StageKey;
    if (sourceStage === destinationStage && result.destination.index === result.source.index) {
      return;
    }

    const previousBoard = board;
    const sourceItems = Array.from(previousBoard[sourceStage] ?? []);
    const destinationItems = Array.from(previousBoard[destinationStage] ?? []);
    const [moved] = sourceItems.splice(result.source.index, 1);
    const updated = { ...moved, stage: destinationStage };
    destinationItems.splice(result.destination.index, 0, updated);

    const nextBoard = {
      ...previousBoard,
      [sourceStage]: sourceItems,
      [destinationStage]: destinationItems,
    };
    setBoard(nextBoard);

    stageMutation.mutate({ id: moved.id, stage: destinationStage }, { onError: () => setBoard(previousBoard) });
  };

  const selectedApplication = useMemo(() => {
    if (!selectedApplicationId) {
      return null;
    }
    for (const stage of STAGES) {
      const found = board[stage.key]?.find((item) => item.id === selectedApplicationId);
      if (found) {
        return found;
      }
    }
    return null;
  }, [board, selectedApplicationId]);

  const notes = notesQuery.data ?? [];

  const handleNoteSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedApplication) {
      return;
    }
    const trimmed = noteBody.trim();
    if (!trimmed && !noteFile) {
      return;
    }
    const formData = new FormData();
    if (trimmed) {
      formData.append("body", trimmed);
    }
    if (noteFile) {
      formData.append("attachment", noteFile);
    }
    addNoteMutation.mutate({ applicationId: selectedApplication.id, formData });
  };

  return (
    <section className="space-y-6">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Application Pipeline</h2>
        <p className="mt-2 text-sm text-slate-300">
          Drag opportunities across stages, capture notes, and keep tasks in sync with your progress.
        </p>
      </header>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid gap-4 overflow-x-auto md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-7">
          {STAGES.map((stage) => {
            const items = board[stage.key] ?? [];
            return (
              <Droppable droppableId={stage.key} key={stage.key}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={clsx(
                      "flex min-h-[14rem] flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/30 p-4 transition",
                      snapshot.isDraggingOver && "border-accent/60 bg-accent/10",
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-slate-200">{stage.label}</h3>
                      <span className="text-xs text-slate-500">{items.length}</span>
                    </div>
                    <div className="space-y-3">
                      {items.map((application, index) => (
                        <Draggable draggableId={application.id} index={index} key={application.id}>
                          {(dragProvided, dragSnapshot) => (
                            <article
                              ref={dragProvided.innerRef}
                              {...dragProvided.draggableProps}
                              {...dragProvided.dragHandleProps}
                              onClick={() => setSelectedApplicationId(application.id)}
                              className={clsx(
                                "space-y-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-sm transition hover:border-accent",
                                dragSnapshot.isDragging && "border-accent bg-accent/10",
                                selectedApplicationId === application.id && "border-accent",
                              )}
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <p className="font-semibold text-slate-200">{application.title || "Untitled"}</p>
                                  <p className="text-xs text-slate-400">
                                    {application.company ?? "Unknown company"}
                                  </p>
                                </div>
                                <span className="text-[11px] text-slate-500">
                                  {application.notes_count} note{application.notes_count === 1 ? "" : "s"}
                                </span>
                              </div>
                              {application.tasks.length > 0 && (
                                <ul className="rounded-lg border border-slate-800 bg-slate-950/60 p-2 text-xs text-slate-400">
                                  {application.tasks.slice(0, 3).map((task) => (
                                    <li key={task.id} className="flex items-center justify-between gap-2">
                                      <span>{task.title}</span>
                                      {task.due_at && (
                                        <span className="text-[10px] text-slate-500">
                                          Due {format(new Date(task.due_at), "MMM d")}
                                        </span>
                                      )}
                                    </li>
                                  ))}
                                  {application.tasks.length > 3 && (
                                    <li className="text-[10px] text-slate-500">
                                      +{application.tasks.length - 3} more
                                    </li>
                                  )}
                                </ul>
                              )}
                              {application.url && (
                                <a
                                  href={application.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="inline-flex text-xs text-accent hover:underline"
                                  onClick={(event) => event.stopPropagation()}
                                >
                                  View posting
                                </a>
                              )}
                            </article>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  </div>
                )}
              </Droppable>
            );
          })}
        </div>
      </DragDropContext>

      {selectedApplication && (
        <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950/40 p-6 shadow-lg">
          <header className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">{selectedApplication.title}</h3>
              <p className="text-xs text-slate-400">
                {selectedApplication.company ?? "Unknown company"} • Stage: {selectedApplication.stage}
              </p>
            </div>
            <button
              type="button"
              className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300 transition hover:border-accent"
              onClick={() => setSelectedApplicationId(null)}
            >
              Close
            </button>
          </header>

          <form onSubmit={handleNoteSubmit} className="space-y-3 rounded-xl border border-slate-800 bg-slate-950/30 p-4">
            <label className="block text-xs text-slate-400">
              Add note
              <textarea
                value={noteBody}
                onChange={(event) => setNoteBody(event.target.value)}
                className="mt-2 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-accent"
                rows={3}
                placeholder="Next steps, outcomes, or reminders…"
              />
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-400">
              <input
                type="file"
                onChange={(event) => setNoteFile(event.target.files?.[0] ?? null)}
                className="text-xs"
              />
              {noteFile && <span className="text-slate-300">{noteFile.name}</span>}
            </label>
            <button
              type="submit"
              disabled={addNoteMutation.isPending}
              className="rounded-full border border-accent px-4 py-2 text-xs font-semibold text-accent transition hover:bg-accent hover:text-slate-950 disabled:cursor-default disabled:opacity-60"
            >
              {addNoteMutation.isPending ? "Saving…" : "Save note"}
            </button>
          </form>

          <div className="space-y-3">
            {notesQuery.isLoading ? (
              <p className="text-xs text-slate-400">Loading notes…</p>
            ) : notes.length === 0 ? (
              <p className="text-xs text-slate-400">No notes yet. Add your first update above.</p>
            ) : (
              notes.map((note) => (
                <article key={note.id} className="space-y-2 rounded-lg border border-slate-800 bg-slate-950/50 p-4 text-xs text-slate-300">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200">{note.body ?? "Attachment"}</span>
                    <span className="text-[10px] text-slate-500">
                      {format(new Date(note.created_at), "PPpp")}
                    </span>
                  </div>
                  {note.attachment_url && (
                    <a
                      href={note.attachment_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex text-[11px] text-accent hover:underline"
                    >
                      {note.attachment_name ?? "Download attachment"}
                    </a>
                  )}
                </article>
              ))
            )}
          </div>
        </section>
      )}
    </section>
  );
}
