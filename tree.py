from treelib import Tree
import os

def create_tree(path, tree, parent=None):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        tree.create_node(item, item_path, parent=parent)
        if os.path.isdir(item_path):
            create_tree(item_path, tree, parent=item_path)

def main():
    path = 'C:/Users/kunya/PycharmProjects/DataVolt'
    tree = Tree()
    tree.create_node(os.path.basename(path), path)  # root node
    create_tree(path, tree, parent=path)
    tree.show()

if __name__ == "__main__":
    main()
