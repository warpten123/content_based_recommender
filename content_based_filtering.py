from sklearn.metrics.pairwise import cosine_similarity
import os
import csv
import json
import numpy as np

class ContentBasedFiltering:

    def __init__(self, data_path):
        self.data = None
        self.filepath = data_path
        

    def read_csv_file(self):
        if self.filepath is None:
            raise ValueError("File path is not set. Please set the file path before reading the CSV.")
        
        with open(self.filepath, mode='r') as file:
            reader = csv.reader(file)
            self.data = list(reader)

    def generate_build_matrix(self):
        if self.data is None:
            raise ValueError("Data is not loaded. Please read the CSV file first.")

        #create a 2d array based on the length of the csv file
     

        
        self.headers = ["Gaming", "Office","Editing", "General", "Low Tier","Mid Tier","High Tier","Bulky", "Not Bulky", "Energy Yes", "Energy No"]
        self.list_of_builds = self.data[1:]
        rows,cols = len(self.list_of_builds), len(self.headers)
        self.build_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        # print(self.build_matrix)
       
        for row in range(len(self.headers)):
            for col in range(len(self.list_of_builds)):
                # print(row,col)
                if self.headers[row] in self.list_of_builds[col]:
                    self.build_matrix[col][row] = 1


        self.build_matrix = np.array(self.build_matrix)
        self.store_to_csv(self.build_matrix,"build_matrix.csv")
        
        return self.build_matrix.tolist()
 
    def store_to_csv(self, data,output_path):
        np.savetxt(output_path, data, delimiter=',', fmt='%d')
    
    def load_csv(self, input_path):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"The file {input_path} does not exist.")
        self.data = np.loadtxt(input_path, delimiter=',', dtype=int)
        return self.data

    def generate_recommendations(self, user_input, top_n=5):
        self.load_build_matrix = self.load_csv("build_matrix.csv")
        self.user_vector = np.array(user_input).reshape(1, -1)
        self.similarity_scores = cosine_similarity(self.load_build_matrix, self.user_vector).flatten()

        # Get all indices sorted by similarity in descending order
        sorted_indices = self.similarity_scores.argsort()[::-1]
        
        # Determine highest similarity score
        highest_score = self.similarity_scores[sorted_indices[0]]
        if np.isclose(highest_score, 0.0, rtol=1e-09, atol=1e-09):
            return {"message": "No recommendations found"}


        # Get all indices with that same highest score
        self.top_indices = [i for i in sorted_indices if self.similarity_scores[i] == highest_score]

        with open("build_reco.json", "r") as f:
            self.build_data = json.load(f)["recommendations"]

        self.recommendations = []
        for i in self.top_indices:
            build_index = int(i)+1  # assuming build_index in JSON is 0-based
            build = next((b for b in self.build_data if int(b["build_index"]) == build_index), None)
            if build:
                build_copy = build.copy()
                build_copy["similarity"] = float(self.similarity_scores[i])
                self.recommendations.append(build_copy)
        print(sorted_indices)
        return {"result": self.recommendations,}


    def print_csv_data(self):
        if self.data is None:
            raise ValueError("Data is not loaded. Please read the CSV file first.")
        return self.data
        
    
