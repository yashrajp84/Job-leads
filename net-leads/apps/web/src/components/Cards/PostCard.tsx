export function PostCard({ post }: { post: any }) {
  return (
    <div className="rounded border bg-white p-3">
      <div className="flex justify-between items-start">
        <div>
          <a href={post.url} target="_blank" className="font-medium hover:underline">Post</a>
          <div className="text-sm text-gray-600">{post.platform}</div>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-gray-100">{post.platform}</span>
      </div>
      {post.text ? <p className="text-sm mt-2 line-clamp-3">{post.text}</p> : null}
      <div className="mt-2 text-sm text-gray-500">Actions: Reply idea · Save</div>
    </div>
  )
}

