export const Card = ({ children, ...props }) => (
  <div className="bg-white shadow rounded-lg p-6" {...props}>
    {children}
  </div>
);

export const CardHeader = ({ children, ...props }) => (
  <div className="mb-4" {...props}>{children}</div>
);

export const CardContent = ({ children, ...props }) => (
  <div {...props}>{children}</div>
);
