"use client";

export type ToastTone = "info" | "success" | "error";

export type NotificationToast = {
  id: string;
  message: string;
  tone: ToastTone;
};

type NotificationCandybarProps = {
  toasts: NotificationToast[];
  onDismiss: (toastId: string) => void;
};

export function NotificationCandybar({ toasts, onDismiss }: NotificationCandybarProps) {
  return (
    <div className="notification-candybar" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => (
        <article className={`notification-candybar__toast notification-candybar__toast--${toast.tone}`} key={toast.id}>
          <p>{toast.message}</p>
          <button type="button" onClick={() => onDismiss(toast.id)} aria-label="Dismiss notification">
            <span className="material-symbols-outlined" aria-hidden>
              close
            </span>
          </button>
        </article>
      ))}
    </div>
  );
}
