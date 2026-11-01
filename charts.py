"""Progress chart. Built with matplotlib's Figure class (no pyplot), so the
same function can embed in Tkinter and also save a PNG file."""

from matplotlib.figure import Figure


def build_progress_figure(weights, daily, target, title_suffix=""):
    """Left: weight trend. Right: calories eaten and burned for the last days.

    weights - [(date, kg)]      daily - [(date, eaten, burned)]
    target  - daily calorie target or None
    """
    fig = Figure(figsize=(9.2, 3.6), dpi=100)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    # ---- weight trend
    ax1.set_title("Weight trend" + title_suffix, fontsize=10)
    if weights:
        labels = [d.strftime("%d-%m") for d, _ in weights]
        values = [w for _, w in weights]
        ax1.plot(range(len(values)), values, marker="o", color="#2c6fbb")
        for i, v in enumerate(values):
            ax1.annotate(f"{v:g}", (i, v), textcoords="offset points",
                         xytext=(0, 6), ha="center", fontsize=7)
        step = max(1, len(labels) // 7)
        ax1.set_xticks(range(0, len(labels), step))
        ax1.set_xticklabels(labels[::step], rotation=30, fontsize=7)
        low, high = min(values), max(values)
        pad = max(0.5, (high - low) * 0.3)
        ax1.set_ylim(low - pad, high + pad)
    else:
        ax1.text(0.5, 0.5, "No weight entries yet", ha="center", va="center",
                 transform=ax1.transAxes, color="gray")
        ax1.set_xticks([])
    ax1.set_ylabel("Weight (kg)", fontsize=8)
    ax1.tick_params(axis="y", labelsize=7)
    ax1.grid(alpha=0.3)

    # ---- calories eaten and burned
    ax2.set_title("Calories eaten and burned (last 7 days)", fontsize=10)
    x = list(range(len(daily)))
    eaten = [e for _, e, _ in daily]
    burned = [b for _, _, b in daily]
    ax2.bar([i - 0.2 for i in x], eaten, width=0.4, color="#e8892b", label="Eaten")
    ax2.bar([i + 0.2 for i in x], burned, width=0.4, color="#4a9d5b", label="Burned")
    if target:
        ax2.axhline(target, color="#c0392b", linestyle="--", linewidth=1,
                    label=f"Target ({target:,.0f})")
    ax2.set_xticks(x)
    ax2.set_xticklabels([d.strftime("%d-%m") for d, _, _ in daily], rotation=30, fontsize=7)
    ax2.set_ylabel("Calories (kcal)", fontsize=8)
    ax2.tick_params(axis="y", labelsize=7)
    top = max(eaten + burned + [target or 0, 100])
    ax2.set_ylim(0, top * 1.28)
    ax2.legend(fontsize=7, loc="upper center", ncol=3)
    ax2.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return fig
