from anytree import Node
from utils.logger import get_logger

class IctLogParser:
    """
    A parser class to convert a structured log file into a tree hierarchy.
    
    Attributes
    ----------
    log_str : str
        The content of the log file read from the given path.

    Methods
    -------
    build_tree(parent_node: Node = None) -> str
        recursively builds a nested tree from the parent node using the remaining log_str
        until its len is 0.
    """

    def __init__(self, path: str) -> None:
        """
        Initializes the TreeLog with the content of the log file.

        Parameters
        ----------
        path : str
            The file path of the log file to be parsed.
        """
        self.path = path
        self.logger = get_logger(__name__)
        with open(path, 'r') as f:
            self.log_str = f.read()

    def _extract_node_name(self, log_str: str):
        """
        Extracts the name of the node from a log string segment.
        
        Parameters
        ----------
        log_str : str
            A segment of the log string.
        
        Returns
        -------
        tuple
            Tuple containing node name and the remaining part of the log string.
        """
        try:
            node_name = ""
            while len(log_str) > 0 and log_str[0] != '|':
                node_name += log_str[0]
                log_str = log_str[1:]
            return node_name, log_str[1:]
        except Exception as e:
            self.logger.debug(f"log that caused the error: {self.path}")
            self.logger.error(e)

    def _create_unique_node(self, node_name: str, parent_node: Node, sibling_count: dict) -> Node:
        """
        Creates a unique tree node based on the node name and the count of its siblings.
        
        Parameters
        ----------
        node_name : str
            Name of the node to be created.
        parent_node : Node
            The parent node of the node being created.
        sibling_count : dict
            A dictionary to keep track of the count of sibling nodes.
        
        Returns
        -------
        Node
            A new unique Node.
        """
        try:
                
            count = sibling_count.get(node_name, 0)
            unique_node_name = f"{node_name}_{count}" if count > 0 else node_name
            sibling_count[node_name] = count + 1
            return Node(unique_node_name, parent=parent_node, data="")
        except Exception as e:
            self.logger.debug(f"log file that caused the error: {self.path}")
            self.logger.error(e)

    def build_tree(self, parent_node: Node = None) -> str:
        """
        builds a nested tree from the parent node using the remaining log_str.
        
        Parameters
        ----------
        parent_node : Node, optional
            The parent node for the current log string segment. Defaults to None.
        
        Returns
        -------
        str
            Remaining log string after parsing.
        """

        try:
            sibling_count = {}  # Reset count for each new set of sibling nodes
            buffer = ""

            while len(self.log_str) > 0:
                char = self.log_str[0]
                self.log_str = self.log_str[1:]

                if char == '{':
                    node_name, self.log_str = self._extract_node_name(self.log_str)
                    node = self._create_unique_node(node_name, parent_node, sibling_count)
                    self.log_str = self.build_tree(node) # Updates the remaining log_str and recursively keeps building the tree

                elif char == '}':
                    if buffer:
                        parent_node.data = buffer.strip()
                        buffer = ""
                    return self.log_str
                else:
                    buffer += char
            if buffer:
                parent_node.data = buffer.strip()
            return self.log_str
        except Exception as e:
            self.logger.debug(f"log file that raised the error: {self.path}")
            self.logger.error(e)


def file_to_tree(log_file_path:str, out_tree:Node):
    ict_log_parser = IctLogParser(log_file_path)
    ict_log_parser.build_tree(out_tree)
