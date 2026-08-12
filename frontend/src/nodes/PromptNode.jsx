import { Handle, Position } from '@xyflow/react';

export function PromptNode({ data }) {
  return (
    <div className="bg-white border-2 border-slate-200 rounded-lg p-4 shadow-sm w-64">
      <Handle type="target" position={Position.Top} />
      <div className="font-bold text-sm mb-2 text-slate-700">AI Decision Node</div>
      <textarea
        className="w-full text-sm p-2 border border-slate-200 rounded resize-none"
        rows="3"
        placeholder="Enter prompt..."
        value={data.prompt}
        onChange={(e) => data.onChange(data.id, e.target.value)}
      />
      <div className="flex justify-between mt-2 text-xs font-semibold">
        <span className="text-green-600">YES</span>
        <span className="text-red-600">NO</span>
      </div>
      <Handle type="source" position={Position.Bottom} id="yes" style={{ left: '25%', background: '#16a34a' }} />
      <Handle type="source" position={Position.Bottom} id="no" style={{ left: '75%', background: '#dc2626' }} />
    </div>
  );
}
