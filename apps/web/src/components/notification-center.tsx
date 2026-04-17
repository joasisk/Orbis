"use client";

export type ReminderEvent = {
  id: string;
  daily_schedule_id: string | null;
  daily_schedule_item_id: string | null;
  delivery_channel: "in_app" | "email" | "push";
  response_status: "pending" | "acknowledged" | "snoozed" | "dismissed";
  sent_at: string;
  responded_at: string | null;
  response_delay_seconds: number | null;
};

type ReminderResponseAction = "acknowledged" | "snoozed" | "dismissed";

type NotificationCenterProps = {
  isOpen: boolean;
  isLoading: boolean;
  error: string;
  notifications: ReminderEvent[];
  onClose: () => void;
  onRespond: (notificationId: string, action: ReminderResponseAction) => Promise<void>;
};

const formatWhen = (sentAt: string) =>
  new Date(sentAt).toLocaleString(undefined, {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  });

export function NotificationCenter({
  isOpen,
  isLoading,
  error,
  notifications,
  onClose,
  onRespond,
}: NotificationCenterProps) {
  if (!isOpen) return null;

  return (
    <section className="notification-center" aria-label="Notification center">
      <header className="notification-center__header">
        <div>
          <p className="stamp-label">Inbox</p>
          <h2 className="headline">Notifications</h2>
        </div>
        <button className="notification-center__close" onClick={onClose} type="button" aria-label="Close notifications">
          <span className="material-symbols-outlined" aria-hidden>
            close
          </span>
        </button>
      </header>

      {isLoading ? <p className="body-copy">Loading reminders…</p> : null}
      {error ? <p className="message-error">{error}</p> : null}

      {!isLoading && !error && notifications.length === 0 ? (
        <p className="body-copy">No pending reminders right now.</p>
      ) : (
        <ul className="notification-center__list">
          {notifications.map((notification) => (
            <li className="notification-center__item" key={notification.id}>
              <p className="notification-center__title">Schedule reminder</p>
              <p className="notification-center__meta">{formatWhen(notification.sent_at)}</p>
              <p className="notification-center__meta">
                Channel: {notification.delivery_channel.replace("_", " ")}
                {notification.daily_schedule_item_id ? ` · Item ${notification.daily_schedule_item_id.slice(0, 8)}` : ""}
              </p>
              <div className="notification-center__actions">
                <button className="btn btn-primary" type="button" onClick={() => void onRespond(notification.id, "acknowledged")}>
                  Ack
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => void onRespond(notification.id, "snoozed")}>
                  Snooze
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => void onRespond(notification.id, "dismissed")}>
                  Dismiss
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
