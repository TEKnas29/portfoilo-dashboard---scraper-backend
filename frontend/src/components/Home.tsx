import { blogPosts } from "../Constants";

const Home = () => {
  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-8">
        {/* Page Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-10">Home</h1>

        {/* Top Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg p-6 border shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-2">Get started</h3>
            <p className="text-gray-600 text-sm mb-4">
              Read our getting started guide to get the most out of your
              Capitalmind subscription.
            </p>
            <button className="text-teal-600 hover:text-teal-700 text-sm font-medium">
              Learn more →
            </button>
          </div>

          <div className="bg-white rounded-lg p-6 border shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-2">Community</h3>
            <p className="text-gray-600 text-sm mb-4">
              Join the conversation on our exclusive community on Slack for
              Capitalmind Premium subscribers
            </p>
            <button className="text-teal-600 hover:text-teal-700 text-sm font-medium">
              Join community →
            </button>
          </div>

          <div className="bg-white rounded-lg p-6 border shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-2">Visit website</h3>
            <p className="text-gray-600 text-sm mb-4">
              Keep up with our latest content on our website
            </p>
            <button className="text-teal-600 hover:text-teal-700 text-sm font-medium">
              Visit site →
            </button>
          </div>
        </div>

        {/* Latest Posts */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-6">Latest Posts</h2>

          <div className="grid md:grid-cols-2 gap-10">
            {blogPosts.map((post) => (
              <article key={post.id}>
                <span className="block text-sm text-gray-500 mb-2">
                  {post.date}
                </span>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 hover:text-teal-600 cursor-pointer">
                  {post.title}
                </h3>
                <p className="text-gray-600 text-sm mb-3 leading-relaxed">
                  {post.excerpt}
                </p>
                <button className="text-teal-600 hover:text-teal-700 text-sm font-medium">
                  Read full post →
                </button>
              </article>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
