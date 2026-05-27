/**
 * Hermes Memory Manager — Dashboard Plugin
 *
 * View and edit Hermes persistent memory files: MEMORY.md and USER.md.
 *
 * Plain IIFE, no build step. Uses window.__HERMES_PLUGIN_SDK__ for React +
 * shadcn primitives. Bundle is pre-built and the plugin_api.py backend
 * handles all file I/O against ~/.hermes/memories/.
 */

(function () {
  "use strict";

  var SDK = window.__HERMES_PLUGIN_SDK__;
  if (!SDK) return;
  var React = SDK.React;
  var h = React.createElement;
  var hooks = SDK.hooks;
  var useState = hooks.useState;
  var useEffect = hooks.useEffect;
  var components = SDK.components;
  var Button = components.Button;
  var Separator = components.Separator;

  var API = "/api/plugins/memory-manager";
  var MEMORY_FILES = ["MEMORY", "USER"];

  // ── API ─────────────────────────────────────────────────────────────────────

  function apiRead(name) {
    return SDK.fetchJSON(API + "/files/" + encodeURIComponent(name));
  }

  function apiWrite(name, content) {
    return SDK.fetchJSON(API + "/files/" + encodeURIComponent(name), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: content }),
    });
  }

  // ── Memory Tab ─────────────────────────────────────────────────────────────

  function MemoryTab(props) {
    var name = props.name;
    var onBack = props.onBack;

    var contentSt = useState("");
    var setContent = contentSt[1];
    var content = contentSt[0];

    var loadingSt = useState(true);
    var setLoading = loadingSt[1];
    var loading = loadingSt[0];

    var savingSt = useState(false);
    var setSaving = savingSt[1];
    var saving = savingSt[0];

    var editModeSt = useState(false);
    var setEditMode = editModeSt[1];
    var editMode = editModeSt[0];

    var msgSt = useState(null);
    var setMsg = msgSt[1];
    var msg = msgSt[0];

    // Load when tab changes
    useEffect(function () {
      setLoading(true);
      setEditMode(false);
      setMsg(null);
      apiRead(name)
        .then(function (d) {
          setContent(d.content || "");
          setLoading(false);
        })
        .catch(function (e) {
          setMsg({ ok: false, msg: "Failed to load: " + String(e) });
          setLoading(false);
        });
    }, [name]);

    function handleEdit() {
      setEditMode(true);
    }

    function handleSave() {
      setSaving(true);
      setMsg(null);
      apiWrite(name, content)
        .then(function () {
          setMsg({ ok: true, msg: "Saved successfully!" });
          setEditMode(false);
          setSaving(false);
        })
        .catch(function (e) {
          setMsg({ ok: false, msg: "Save failed: " + String(e) });
          setSaving(false);
        });
    }

    return h("div", { className: "flex flex-col h-full" },
      // Header
      h("div", { className: "flex items-center justify-between mb-4" },
        h("div", { className: "flex items-center gap-3" },
          onBack && h(Button, { variant: "ghost", size: "sm", onClick: onBack },
            h("span", { dangerouslySetInnerHTML: { __html: "&larr;" } }), " Back"
          ),
          h("h2", { className: "text-lg font-semibold" }, name + ".md"),
        ),
        h("div", { className: "flex items-center gap-2" },
          !editMode && h(Button, {
            size: "sm",
            variant: "outline",
            onClick: handleEdit,
            disabled: loading,
          }, "Edit"),
          editMode && h(Button, {
            size: "sm",
            variant: "default",
            onClick: handleSave,
            disabled: saving,
          }, saving ? "Saving…" : "Save"),
        ),
      ),

      // Loading
      loading && h("div", { className: "text-sm text-muted-foreground" }, "Loading…"),

      // Error
      msg && !msg.ok && h("div", {
        className: "text-xs px-3 py-2 rounded mb-3 bg-destructive/10 border border-destructive/30 text-destructive"
      }, msg.msg),

      // Success
      msg && msg.ok && h("div", {
        className: "text-xs px-3 py-2 rounded mb-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400"
      }, msg.msg),

      // Content
      !loading && h("div", { className: "flex-1 flex flex-col" },
        editMode
          ? h("textarea", {
              className: "flex-1 w-full bg-transparent border border-input rounded p-3 text-sm font-mono resize-y",
              value: content,
              onChange: function (e) { setContent(e.target.value); },
              style: { fontFamily: "inherit", minHeight: "400px" },
            })
          : h("pre", {
              className: "flex-1 text-sm bg-muted/50 rounded p-4 overflow-auto whitespace-pre-wrap font-mono",
              style: { fontFamily: "inherit", minHeight: "400px" },
            }, content || "(empty)"),
      ),
    );
  }

  // ── Main App ──────────────────────────────────────────────────────────────

  function MemoryManagerApp() {
    var activeTabSt = useState("MEMORY");
    var activeTab = activeTabSt[0];

    return h("div", { className: "p-6 max-w-5xl mx-auto h-full flex flex-col" },
      h("div", { className: "mb-4" },
        h("h1", { className: "text-xl font-bold mb-1" }, "Memory Manager"),
        h("p", { className: "text-sm text-muted-foreground" },
          "View and edit your Hermes persistent memory files."
        ),
      ),

      // Tab buttons
      h("div", { className: "flex gap-1 mb-4 bg-muted/50 p-1 rounded-lg w-fit" },
        MEMORY_FILES.map(function (tab) {
          return h("button", {
            key: tab,
            onClick: function () { activeTabSt[1](tab); },
            className: "px-4 py-1.5 text-sm rounded-md transition-colors " +
              (activeTab === tab
                ? "bg-background shadow-sm font-medium"
                : "text-muted-foreground hover:text-foreground"),
          }, tab);
        }),
      ),

      h(Separator, { className: "mb-4" }),

      // Tab content
      h("div", { className: "flex-1 overflow-auto" },
        h(MemoryTab, { name: activeTab }),
      ),
    );
  }

  // ── Register ──────────────────────────────────────────────────────────────

  window.__HERMES_PLUGINS__.register("memory-manager", MemoryManagerApp);
})();