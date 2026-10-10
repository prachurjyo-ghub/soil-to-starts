export default function SkeletonPage({ dashboard = false }) {
  return (
    <div className={dashboard ? "skeleton-page skeleton-dashboard" : "skeleton-page"} aria-label="Loading content" role="status">
      {dashboard && <div className="skeleton-side skeleton-shimmer" />}
      <div className="skeleton-content">
        <div className="skeleton-nav skeleton-shimmer" />
        <div className="skeleton-kicker skeleton-shimmer" />
        <div className="skeleton-title skeleton-shimmer" />
        <div className="skeleton-title short skeleton-shimmer" />
        <div className="skeleton-copy skeleton-shimmer" />
        <div className="skeleton-grid">
          {[0, 1, 2].map((item) => <div className="skeleton-card skeleton-shimmer" key={item} />)}
        </div>
      </div>
      <span className="sr-only">Loading…</span>
    </div>
  );
}
