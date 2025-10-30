"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useSession } from "next-auth/react";

import { getJson, patchJson } from "@/lib/api-client";

type TaskItem = {
  id: string;
  title: string;
  type: string | null;
  priority: "low" | "normal" | "high" | "urgent";
  due_at: string | null;
  completed_at: string | null;
  application_id: string | null;
  application_title: string | null;
};

export default function TasksPage() {
  const queryClient = useQueryClient();
  const { data: session } = useSession();
  const userId = session?.user?.id;

  const tasksQuery = useQuery({
    enabled: Boolean(userId),
    queryKey: ["tasks", userId],
    queryFn: async () => getJson<TaskItem[]>("/tasks", { userId }),
  });

  const actionMutation = useMutation({
    mutationFn: async (variables: { id: string; action: "complete" | "defer" | "undo" }) =>
      patchJson(`/tasks/${variables.id}`, { action: variables.action }, { userId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", userId] });
    },
  });

  const tasks = tasksQuery.data ?? [];
  const todo = tasks.filter((task) => !task.completed_at);
  const completed = tasks.filter((task) => task.completed_at);

  const renderTask = (task: TaskItem, status: "open" | "done") => (
    <article
      key={task.id}
      className="space-y-2 rounded-xl border border-slate-800 bg-slate-950/50 p-4 text-sm text-slate-200"
    >
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold text-slate-200">{task.title}</h3>
        <span className="text-xs uppercase text-slate-500">{task.priority}</span>
      </div>
      {task.application_title && (
        <p className="text-xs text-slate-400">Linked to {task.application_title}</p>
      )}
      {task.due_at && (
        <p className="text-xs text-slate-400">
          Due {format(new Date(task.due_at), "PPpp")}
        </p>
      )}
      <div className="flex flex-wrap items-center gap-2">
        {status === "open" ? (
          <>
            <button
              type="button"
              onClick={() => actionMutation.mutate({ id: task.id, action: "complete" })}
              className="rounded-full border border-emerald-500/60 px-3 py-1 text-xs text-emerald-200 transition hover:bg-emerald-500/10"
            >
              Mark done
            </button>
            <button
              type="button"
              onClick={() => actionMutation.mutate({ id: task.id, action: "defer" })}
              className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300 transition hover:border-accent hover:text-accent"
            >
              Defer 2 days
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={() => actionMutation.mutate({ id: task.id, action: "undo" })}
            className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300 transition hover:border-accent hover:text-accent"
          >
            Undo
          </button>
        )}
      </div>
    </article>
  );

  return (
    <section className="space-y-6">
      <header className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 shadow-xl">
        <h2 className="text-xl font-semibold">Task Inbox</h2>
        <p className="mt-2 text-sm text-slate-300">
          Knock out follow-ups, interview prep, and reminders generated as you move applications through the pipeline.
        </p>
      </header>

      {tasksQuery.isLoading ? (
        <p className="text-sm text-slate-400">Loading tasks…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3 rounded-2xl border border-slate-800 bg-slate-950/30 p-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-200">To do</h3>
              <span className="text-xs text-slate-500">{todo.length}</span>
            </div>
            {todo.length === 0 ? (
              <p className="text-xs text-slate-400">You're caught up for now.</p>
            ) : (
              todo.map((task) => renderTask(task, "open"))
            )}
          </div>
          <div className="space-y-3 rounded-2xl border border-slate-800 bg-slate-950/30 p-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-200">Completed</h3>
              <span className="text-xs text-slate-500">{completed.length}</span>
            </div>
            {completed.length === 0 ? (
              <p className="text-xs text-slate-400">No completed tasks yet.</p>
            ) : (
              completed.map((task) => renderTask(task, "done"))
            )}
          </div>
        </div>
      )}
    </section>
  );
}
