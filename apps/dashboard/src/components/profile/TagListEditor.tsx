import { X } from 'lucide-react';

interface TagListEditorProps {
  label: string;
  description?: string;
  items: string[];
  placeholder?: string;
  onChange: (items: string[]) => void;
}

export default function TagListEditor({
  label,
  description,
  items,
  placeholder = 'Add item…',
  onChange,
}: TagListEditorProps) {
  const addItem = (raw: string) => {
    const value = raw.trim();
    if (!value || items.includes(value)) return;
    onChange([...items, value]);
  };

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          {label}
        </h3>
        {description ? (
          <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">{description}</p>
        ) : null}
      </div>
      <form
        className="flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          const form = event.currentTarget;
          const input = form.elements.namedItem('tag-input') as HTMLInputElement;
          addItem(input.value);
          input.value = '';
        }}
      >
        <input
          name="tag-input"
          type="text"
          placeholder={placeholder}
          className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none flex-1 max-w-sm"
        />
        <button
          type="submit"
          className="bg-slate-900 text-white text-xs px-4 py-2 rounded-lg font-semibold hover:bg-slate-800"
        >
          Add
        </button>
      </form>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <span
            key={item}
            className="bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs px-2.5 py-1 rounded-md flex items-center gap-1.5 font-medium"
          >
            {item}
            <button
              type="button"
              onClick={() => onChange(items.filter((entry) => entry !== item))}
              className="text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-400"
              aria-label={`Remove ${item}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}
