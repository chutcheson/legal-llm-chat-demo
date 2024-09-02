export const Select = ({ children, ...props }) => (
  <select className="p-2 border rounded" {...props}>{children}</select>
);

export const SelectContent = ({ children, ...props }) => (
  <optgroup {...props}>{children}</optgroup>
);

export const SelectItem = ({ children, value, ...props }) => (
  <option value={value} {...props}>{children}</option>
);

export const SelectTrigger = ({ children, ...props }) => (
  <div {...props}>{children}</div>
);

export const SelectValue = ({ children, ...props }) => (
  <span {...props}>{children}</span>
);
