class GoogleLinkNode:
    __nodes = []

    def __init__(self, link):
        self.link = link
        self.__internalLinks = []
        self.__externalLinks = []
        pass

    @staticmethod
    def add_to_google_link_node_storage(node):
        GoogleLinkNode.__nodes.append(node)
    
    def add_to_internal_link(self, link):
        if(link in self.__internalLinks):
            print('이미 존재하는 내부 link 입니다.')
            return
        self.__internalLinks.append(link)

    def add_to_external_link(self, link):
        if(link in self.__externalLinks):
            print('이미 존재하는 외부 link 입니다.')
            return
        self.__externalLinks.append(link)

    def get_internal_links(self):
        return self.__internalLinks
    
    def get_external_links(self):
        return self.__externalLinks
        
    @staticmethod
    def get_nodes():
        return GoogleLinkNode.__nodes

# g1 = GoogleLinkNode(123)
# g2 = GoogleLinkNode(123)

# GoogleLinkNode.add_to_google_link_node_storage(g1)
# GoogleLinkNode.add_to_google_link_node_storage(g2)

# nodes = GoogleLinkNode.get_nodes()

# for i in nodes:
#     print(i.link)