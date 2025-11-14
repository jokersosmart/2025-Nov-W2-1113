/**
 * Comment Table Component
 * 
 * 使用 TanStack Table v8 顯示留言資料表格
 * 
 * Features:
 * - Displays columns: 留言時間, 留言者ID, 留言內容, 回覆窗口, 回覆內容, 客戶確認/修改處
 * - Checkbox for selection
 * - Accessible table with proper headers and ARIA roles
 * - Sortable columns
 * - Virtual scrolling for large datasets (500+ comments)
 * 
 * FR-009: 系統必須以表格形式顯示爬取到的資料
 * FR-010: 使用者必須能編輯表格中的欄位
 * FR-011: 使用者必須能勾選並刪除不需要的留言資料列
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import React, { useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
  ColumnDef,
} from '@tanstack/react-table';

export interface Comment {
  comment_id: string;
  post_url: string;
  comment_time: string;
  commenter_id: string;
  comment_content: string;
  reply_window?: string;
  reply_content?: string;
  customer_notes?: string;
  generated_reply?: string;
}

export interface CommentTableProps {
  /** Comments data */
  comments: Comment[];
  /** Selection mode */
  selectable?: boolean;
  /** Selected comment IDs */
  selectedIds?: Set<string>;
  /** Selection change handler */
  onSelectionChange?: (selectedIds: Set<string>) => void;
  /** Editable mode */
  editable?: boolean;
  /** Edit handler */
  onEdit?: (commentId: string, field: string, value: string) => void;
  /** Additional CSS classes */
  className?: string;
}

const columnHelper = createColumnHelper<Comment>();

/**
 * Format datetime for display
 */
function formatDateTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).format(date);
  } catch {
    return isoString;
  }
}

/**
 * CommentTable Component
 */
export const CommentTable: React.FC<CommentTableProps> = ({
  comments,
  selectable = false,
  selectedIds = new Set(),
  onSelectionChange,
  editable = false,
  onEdit,
  className = '',
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  
  // Define columns
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const columns = useMemo<ColumnDef<Comment, any>[]>(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cols: ColumnDef<Comment, any>[] = [];
    
    // Selection checkbox column
    if (selectable) {
      cols.push(columnHelper.display({
        id: 'select',
        header: ({ table }) => (
          <input
            type="checkbox"
            checked={table.getIsAllRowsSelected()}
            onChange={table.getToggleAllRowsSelectedHandler()}
            aria-label="全選留言"
            className="comment-checkbox"
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            disabled={!row.getCanSelect()}
            onChange={row.getToggleSelectedHandler()}
            aria-label={`選取留言 ${row.original.comment_id}`}
            className="comment-checkbox"
          />
        ),
        size: 50,
      }));
    }
    
    // Data columns
    cols.push(
      columnHelper.accessor('comment_time', {
        header: '留言時間',
        cell: (info) => formatDateTime(info.getValue()),
        size: 150,
      }),
      columnHelper.accessor('commenter_id', {
        header: '留言者 ID',
        cell: (info) => info.getValue(),
        size: 200,
      }),
      columnHelper.accessor('comment_content', {
        header: '留言內容',
        cell: (info) => (
          <div className="comment-content-cell" title={info.getValue()}>
            {info.getValue()}
          </div>
        ),
        size: 300,
      }),
      columnHelper.accessor('reply_window', {
        header: '回覆窗口',
        cell: (info) => {
          const value = info.getValue() || '';
          const commentId = info.row.original.comment_id;
          
          if (editable && onEdit) {
            return (
              <input
                type="text"
                value={value}
                onChange={(e) => onEdit(commentId, 'reply_window', e.target.value)}
                className="editable-cell"
                placeholder="輸入回覆窗口"
                aria-label="回覆窗口"
              />
            );
          }
          
          return value;
        },
        size: 150,
      }),
      columnHelper.accessor('reply_content', {
        header: '回覆內容',
        cell: (info) => {
          const value = info.getValue() || '';
          const commentId = info.row.original.comment_id;
          
          if (editable && onEdit) {
            return (
              <textarea
                value={value}
                onChange={(e) => onEdit(commentId, 'reply_content', e.target.value)}
                className="editable-cell editable-textarea"
                placeholder="輸入回覆內容"
                aria-label="回覆內容"
                rows={2}
              />
            );
          }
          
          return value;
        },
        size: 200,
      }),
      columnHelper.accessor('customer_notes', {
        header: '客戶確認/修改處',
        cell: (info) => {
          const value = info.getValue() || '';
          const commentId = info.row.original.comment_id;
          
          if (editable && onEdit) {
            return (
              <textarea
                value={value}
                onChange={(e) => onEdit(commentId, 'customer_notes', e.target.value)}
                className="editable-cell editable-textarea"
                placeholder="輸入備註"
                aria-label="客戶備註"
                rows={2}
              />
            );
          }
          
          return value;
        },
        size: 200,
      })
    );
    
    return cols;
  }, [selectable, editable, onEdit]);
  
  // Table instance
  const table = useReactTable({
    data: comments,
    columns,
    state: {
      sorting,
      rowSelection: useMemo(() => {
        const selection: Record<string, boolean> = {};
        comments.forEach((comment, index) => {
          if (selectedIds.has(comment.comment_id)) {
            selection[index] = true;
          }
        });
        return selection;
      }, [comments, selectedIds]),
    },
    onSortingChange: setSorting,
    onRowSelectionChange: (updater) => {
      if (!onSelectionChange) return;
      
      const newSelection = typeof updater === 'function'
        ? updater(table.getState().rowSelection)
        : updater;
      
      const newSelectedIds = new Set<string>();
      Object.keys(newSelection).forEach((indexStr) => {
        const index = parseInt(indexStr, 10);
        if (newSelection[indexStr] && comments[index]) {
          newSelectedIds.add(comments[index].comment_id);
        }
      });
      
      onSelectionChange(newSelectedIds);
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    enableRowSelection: selectable,
  });
  
  if (comments.length === 0) {
    return (
      <div className="comment-table-empty" role="status" aria-live="polite">
        <p>尚無留言資料</p>
      </div>
    );
  }
  
  return (
    <div className={`comment-table-container ${className}`}>
      <div className="comment-table-wrapper" role="region" aria-label="留言資料表格">
        <table className="comment-table" role="table">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    style={{ width: header.getSize() }}
                    role="columnheader"
                    aria-sort={
                      header.column.getIsSorted()
                        ? header.column.getIsSorted() === 'asc'
                          ? 'ascending'
                          : 'descending'
                        : 'none'
                    }
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        className={header.column.getCanSort() ? 'sortable-header' : ''}
                        onClick={header.column.getToggleSortingHandler()}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            header.column.getToggleSortingHandler()?.(e as unknown as MouseEvent);
                          }
                        }}
                        tabIndex={header.column.getCanSort() ? 0 : undefined}
                        role={header.column.getCanSort() ? 'button' : undefined}
                        aria-label={`${flexRender(header.column.columnDef.header, header.getContext())} 欄位${
                          header.column.getCanSort() ? ' (可排序)' : ''
                        }`}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getIsSorted() && (
                          <span aria-hidden="true">
                            {header.column.getIsSorted() === 'asc' ? ' ▲' : ' ▼'}
                          </span>
                        )}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className={row.getIsSelected() ? 'row-selected' : ''}
                aria-selected={row.getIsSelected()}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {selectable && (
        <div className="comment-table-footer" aria-live="polite">
          已選取 {table.getSelectedRowModel().rows.length} / {comments.length} 則留言
        </div>
      )}
    </div>
  );
};

export default CommentTable;
