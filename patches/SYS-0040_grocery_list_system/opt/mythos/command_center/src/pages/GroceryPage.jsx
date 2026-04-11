import { useState, useEffect, useCallback } from "react";

const API_BASE = window.location.origin;

export default function GroceryPage() {
  const [items, setItems] = useState([]);
  const [aisles, setAisles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addText, setAddText] = useState("");
  const [filter, setFilter] = useState("all"); // all, remaining, checked
  const [currentAisle, setCurrentAisle] = useState(null);
  const [shoppingMode, setShoppingMode] = useState(false);

  const fetchList = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/grocery/list`);
      const data = await res.json();
      setItems(data.items || []);
      setAisles(data.aisles || []);
    } catch (e) {
      console.error("Failed to fetch grocery list:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchList(); }, [fetchList]);

  const addItems = async () => {
    if (!addText.trim()) return;
    try {
      await fetch(`${API_BASE}/api/grocery/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: addText }),
      });
      setAddText("");
      fetchList();
    } catch (e) {
      console.error("Failed to add:", e);
    }
  };

  const toggleCheck = async (itemId, currentChecked) => {
    try {
      await fetch(`${API_BASE}/api/grocery/check/${itemId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ checked: !currentChecked }),
      });
      setItems(prev => prev.map(i =>
        i.id === itemId ? { ...i, checked: !currentChecked } : i
      ));
    } catch (e) {
      console.error("Failed to toggle:", e);
    }
  };

  const removeItem = async (itemId) => {
    try {
      await fetch(`${API_BASE}/api/grocery/remove/${itemId}`, { method: "DELETE" });
      setItems(prev => prev.filter(i => i.id !== itemId));
    } catch (e) {
      console.error("Failed to remove:", e);
    }
  };

  const clearChecked = async () => {
    try {
      await fetch(`${API_BASE}/api/grocery/clear`, { method: "POST" });
      fetchList();
    } catch (e) {
      console.error("Failed to clear:", e);
    }
  };

  const resetList = async () => {
    if (!window.confirm("Reset entire list and start fresh?")) return;
    try {
      await fetch(`${API_BASE}/api/grocery/reset`, { method: "POST" });
      fetchList();
    } catch (e) {
      console.error("Failed to reset:", e);
    }
  };

  // Group items by aisle
  const grouped = {};
  const filteredItems = items.filter(i => {
    if (filter === "remaining") return !i.checked;
    if (filter === "checked") return i.checked;
    return true;
  });

  filteredItems.forEach(item => {
    const aisle = item.aisle_name || "Other";
    if (!grouped[aisle]) {
      grouped[aisle] = {
        icon: item.aisle_icon || "🛒",
        sort: item.aisle_sort || 99,
        items: []
      };
    }
    grouped[aisle].items.push(item);
  });

  const sortedAisles = Object.entries(grouped).sort((a, b) => a[1].sort - b[1].sort);

  // Shopping mode — find first unchecked aisle
  const uncheckedAisles = sortedAisles.filter(([, g]) => g.items.some(i => !i.checked));

  const totalItems = items.length;
  const checkedItems = items.filter(i => i.checked).length;
  const remainingItems = totalItems - checkedItems;
  const pct = totalItems > 0 ? Math.round((checkedItems / totalItems) * 100) : 0;

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading grocery list...</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🛒 Grocery List</h1>
        <div style={styles.headerActions}>
          <button
            style={{
              ...styles.modeBtn,
              ...(shoppingMode ? styles.modeBtnActive : {})
            }}
            onClick={() => setShoppingMode(!shoppingMode)}
          >
            {shoppingMode ? "📋 Full List" : "🏪 Shopping Mode"}
          </button>
        </div>
      </div>

      {/* Progress bar */}
      {totalItems > 0 && (
        <div style={styles.progressContainer}>
          <div style={styles.progressBar}>
            <div style={{ ...styles.progressFill, width: `${pct}%` }} />
          </div>
          <div style={styles.progressText}>
            {pct}% — {checkedItems}/{totalItems} items ({remainingItems} left)
          </div>
        </div>
      )}

      {/* Add items */}
      <div style={styles.addSection}>
        <input
          type="text"
          style={styles.addInput}
          placeholder="Add items (comma-separated): milk, 2x eggs, bread..."
          value={addText}
          onChange={e => setAddText(e.target.value)}
          onKeyDown={e => e.key === "Enter" && addItems()}
        />
        <button style={styles.addBtn} onClick={addItems}>Add</button>
      </div>

      {/* Filters */}
      {!shoppingMode && (
        <div style={styles.filterRow}>
          {["all", "remaining", "checked"].map(f => (
            <button
              key={f}
              style={{
                ...styles.filterBtn,
                ...(filter === f ? styles.filterBtnActive : {})
              }}
              onClick={() => setFilter(f)}
            >
              {f === "all" ? `All (${totalItems})` :
               f === "remaining" ? `Remaining (${remainingItems})` :
               `Checked (${checkedItems})`}
            </button>
          ))}
          <div style={styles.filterSpacer} />
          {checkedItems > 0 && (
            <button style={styles.clearBtn} onClick={clearChecked}>
              🧹 Clear Checked
            </button>
          )}
          <button style={styles.resetBtn} onClick={resetList}>🔄 Reset</button>
        </div>
      )}

      {/* Shopping mode — one aisle at a time */}
      {shoppingMode ? (
        <div style={styles.shoppingMode}>
          {uncheckedAisles.length === 0 ? (
            <div style={styles.doneMsg}>
              🎉 All done! Everything is checked off.
            </div>
          ) : (
            <>
              <div style={styles.aisleNav}>
                <span style={styles.aisleNavText}>
                  {uncheckedAisles.length} aisle{uncheckedAisles.length !== 1 ? 's' : ''} remaining
                </span>
              </div>
              {(() => {
                const [aisleName, aisleData] = uncheckedAisles[currentAisle || 0] || uncheckedAisles[0];
                return (
                  <div style={styles.aisleCard}>
                    <div style={styles.aisleHeader}>
                      <span style={styles.aisleIcon}>{aisleData.icon}</span>
                      <h2 style={styles.aisleName}>{aisleName}</h2>
                      <span style={styles.aisleCount}>
                        {aisleData.items.filter(i => !i.checked).length} items
                      </span>
                    </div>
                    <div style={styles.aisleItems}>
                      {aisleData.items.map(item => (
                        <div
                          key={item.id}
                          style={{
                            ...styles.itemRow,
                            ...(item.checked ? styles.itemChecked : {})
                          }}
                          onClick={() => toggleCheck(item.id, item.checked)}
                        >
                          <span style={styles.checkbox}>
                            {item.checked ? "✅" : "⬜"}
                          </span>
                          <span style={{
                            ...styles.itemName,
                            ...(item.checked ? styles.itemNameChecked : {})
                          }}>
                            {item.name}
                          </span>
                          {item.quantity !== "1" && (
                            <span style={styles.itemQty}>×{item.quantity}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}
              <div style={styles.aisleNavButtons}>
                <button
                  style={styles.navBtn}
                  disabled={!currentAisle || currentAisle === 0}
                  onClick={() => setCurrentAisle(Math.max(0, (currentAisle || 0) - 1))}
                >
                  ← Previous Aisle
                </button>
                <button
                  style={styles.navBtn}
                  disabled={(currentAisle || 0) >= uncheckedAisles.length - 1}
                  onClick={() => setCurrentAisle(Math.min(uncheckedAisles.length - 1, (currentAisle || 0) + 1))}
                >
                  Next Aisle →
                </button>
              </div>
            </>
          )}
        </div>
      ) : (
        /* Full list mode */
        <div style={styles.listContainer}>
          {sortedAisles.length === 0 ? (
            <div style={styles.emptyMsg}>
              Your list is empty. Add items above to get started!
            </div>
          ) : (
            sortedAisles.map(([aisleName, aisleData]) => (
              <div key={aisleName} style={styles.aisleSection}>
                <div style={styles.aisleSectionHeader}>
                  <span style={styles.aisleIcon}>{aisleData.icon}</span>
                  <h3 style={styles.aisleSectionName}>{aisleName}</h3>
                  <span style={styles.aisleSectionCount}>
                    {aisleData.items.filter(i => !i.checked).length}/{aisleData.items.length}
                  </span>
                </div>
                {aisleData.items.map(item => (
                  <div
                    key={item.id}
                    style={{
                      ...styles.itemRow,
                      ...(item.checked ? styles.itemChecked : {})
                    }}
                  >
                    <span
                      style={styles.checkbox}
                      onClick={() => toggleCheck(item.id, item.checked)}
                    >
                      {item.checked ? "✅" : "⬜"}
                    </span>
                    <span style={{
                      ...styles.itemName,
                      ...(item.checked ? styles.itemNameChecked : {})
                    }}>
                      {item.name}
                    </span>
                    {item.quantity !== "1" && (
                      <span style={styles.itemQty}>×{item.quantity}</span>
                    )}
                    <button
                      style={styles.removeBtn}
                      onClick={() => removeItem(item.id)}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 700,
    margin: "0 auto",
    padding: "20px",
    fontFamily: "'Segoe UI', system-ui, sans-serif",
  },
  loading: {
    textAlign: "center",
    padding: 40,
    color: "#888",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    margin: 0,
  },
  headerActions: {
    display: "flex",
    gap: 8,
  },
  modeBtn: {
    padding: "8px 16px",
    border: "2px solid #333",
    borderRadius: 8,
    background: "transparent",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 14,
  },
  modeBtnActive: {
    background: "#333",
    color: "#fff",
  },
  progressContainer: {
    marginBottom: 16,
  },
  progressBar: {
    height: 8,
    background: "#e0e0e0",
    borderRadius: 4,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "linear-gradient(90deg, #4CAF50, #8BC34A)",
    borderRadius: 4,
    transition: "width 0.3s ease",
  },
  progressText: {
    fontSize: 13,
    color: "#666",
    marginTop: 4,
  },
  addSection: {
    display: "flex",
    gap: 8,
    marginBottom: 16,
  },
  addInput: {
    flex: 1,
    padding: "10px 14px",
    border: "2px solid #ddd",
    borderRadius: 8,
    fontSize: 14,
    outline: "none",
  },
  addBtn: {
    padding: "10px 20px",
    background: "#4CAF50",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 14,
  },
  filterRow: {
    display: "flex",
    gap: 8,
    marginBottom: 16,
    alignItems: "center",
    flexWrap: "wrap",
  },
  filterBtn: {
    padding: "6px 12px",
    border: "1px solid #ddd",
    borderRadius: 6,
    background: "#f5f5f5",
    cursor: "pointer",
    fontSize: 13,
  },
  filterBtnActive: {
    background: "#333",
    color: "#fff",
    borderColor: "#333",
  },
  filterSpacer: { flex: 1 },
  clearBtn: {
    padding: "6px 12px",
    border: "1px solid #ff9800",
    borderRadius: 6,
    background: "transparent",
    cursor: "pointer",
    fontSize: 13,
    color: "#ff9800",
  },
  resetBtn: {
    padding: "6px 12px",
    border: "1px solid #f44336",
    borderRadius: 6,
    background: "transparent",
    cursor: "pointer",
    fontSize: 13,
    color: "#f44336",
  },
  listContainer: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  aisleSection: {
    border: "1px solid #e0e0e0",
    borderRadius: 10,
    overflow: "hidden",
  },
  aisleSectionHeader: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "10px 14px",
    background: "#f8f8f8",
    borderBottom: "1px solid #e0e0e0",
  },
  aisleSectionName: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600,
    flex: 1,
  },
  aisleSectionCount: {
    fontSize: 13,
    color: "#888",
  },
  itemRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 14px",
    borderBottom: "1px solid #f0f0f0",
    cursor: "pointer",
    transition: "background 0.15s",
  },
  itemChecked: {
    background: "#f9f9f9",
    opacity: 0.6,
  },
  checkbox: {
    fontSize: 18,
    cursor: "pointer",
    userSelect: "none",
  },
  itemName: {
    flex: 1,
    fontSize: 15,
  },
  itemNameChecked: {
    textDecoration: "line-through",
    color: "#999",
  },
  itemQty: {
    fontSize: 13,
    color: "#666",
    background: "#f0f0f0",
    padding: "2px 6px",
    borderRadius: 4,
  },
  removeBtn: {
    background: "none",
    border: "none",
    color: "#ccc",
    cursor: "pointer",
    fontSize: 16,
    padding: "0 4px",
  },
  emptyMsg: {
    textAlign: "center",
    padding: 40,
    color: "#888",
    fontSize: 15,
  },
  // Shopping mode styles
  shoppingMode: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  doneMsg: {
    textAlign: "center",
    padding: 60,
    fontSize: 20,
    fontWeight: 600,
  },
  aisleNav: {
    textAlign: "center",
    color: "#888",
    fontSize: 14,
  },
  aisleNavText: {},
  aisleCard: {
    border: "2px solid #333",
    borderRadius: 12,
    overflow: "hidden",
  },
  aisleHeader: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "14px 18px",
    background: "#333",
    color: "#fff",
  },
  aisleIcon: {
    fontSize: 24,
  },
  aisleName: {
    margin: 0,
    fontSize: 20,
    fontWeight: 700,
    flex: 1,
  },
  aisleCount: {
    fontSize: 14,
    opacity: 0.8,
  },
  aisleItems: {},
  aisleNavButtons: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
  },
  navBtn: {
    flex: 1,
    padding: "10px 16px",
    border: "2px solid #333",
    borderRadius: 8,
    background: "transparent",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 14,
  },
};
