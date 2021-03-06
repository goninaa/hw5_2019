import json
from typing import Union, Tuple
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """
    
    def __init__(self, data_fname: Union[pathlib.Path, str]):
        if isinstance (data_fname, str):
            self.data_fname = pathlib.Path(data_fname)
        else:
            self.data_fname = data_fname
        if not self.data_fname.is_file():
            raise ValueError ('file does not exists')

    def read_data(self):
        """
        Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        self.data = pd.read_json(self.data_fname)

    def show_age_distrib(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates and plots the age distribution of the participants.
        Returns a tuple containing two numpy arrays:
        The first item being the number of people in a given bin.
        The second item being the bin edges.
        """
        self.plot_hist()
        self.people_in_bin ()

    def plot_hist (self):
        """ plots an histogram """
        ax = self.data[['age']].plot(kind='hist',bins=[0,10,20,30,40,40,50,60,70,80,90,100],rwidth=0.8)
        plt.title ('age distribution')
        plt.xlabel('age')
        plt.ylabel('number of people')
        plt.xticks(np.arange(0, 100, step=10))
        ax.get_legend().remove()
        plt.show()
        
    def people_in_bin (self):
        """ returns the number of people in the bins"""
        bins = pd.IntervalIndex.from_tuples([(0,10), (10,20), (20,30), (30,40),(40,50),(50,60),(60,70),(70,80),(80,90),(90,100)])
        # bins =np.array([0,10,20,30,40,50,60,70,80,90,100])
        people = pd.cut(self.data['age'], bins).value_counts().sort_index().values
        # print (people)
        # print (people[2], bins[2])
        people_bin = (people, bins)
        return people_bin


    def remove_rows_without_mail(self) -> pd.DataFrame:
        """
        Checks self.data for rows with invalid emails, and removes them.
        Returns the corrected DataFrame, i.e. the same table but with
        the erroneous rows removed and the (ordinal) index after a reset.
        """
        valid_email = self.data['email'].str.contains('@' and '.co')
        df_valid_email = self.data.where(valid_email)
        df_valid_email = df_valid_email.dropna(subset=['email'])
        # print (df_valid_email)
        return df_valid_email

    def fill_na_with_mean(self) -> Union[pd.DataFrame, np.ndarray]:
        """
        Finds, in the original DataFrame, the subjects that didn't answer
        all questions, and replaces that missing value with the mean of the
        other grades for that student. Returns the corrected DataFrame,
        as well as the row indices of the students that their new grades
        were generated.
        """
        inds = np.asarray(self.data.loc[:,'q1':'q5'].isnull()).nonzero()[0]
        # print (inds)
        t_rows = self.data.loc[:,'q1':'q5'].T  # transpose relevant rows
        filled_rows = t_rows.fillna(t_rows.mean()).T  # fillna the rows and transpose back
        self.data.loc[:,'q1':'q5'] = filled_rows # replace the rows with the new rows
        # print (self.data)
        
        return filled_rows, inds

    def correlate_gender_age(self) -> pd.DataFrame:
        """
        Looks for a correlation between the gender of the subject, their age
        and the score for all five questions.
        Returns a DataFrame with a MultiIndex containing the gender and whether
        the subject is above 40 years of age, and the average score in each of
        the five questions.
        """
        self.data['over 40'] = self.data['age'] > 40
        gender_age = self.data.groupby(['gender', 'over 40']).mean()
        gender_age.pop('id')
        gender_age.pop('age')
        # print (gender_age)
        # plot:
        gender_age.plot(kind = 'bar')
        plt.title ('Mean question results for different groups (True means above 40)')
        plt.ylabel('Score')
        plt.legend (loc = 1)
        plt.show()
        return gender_age

if __name__ == "__main__":
    data_fname = 'data.json'
    d = QuestionnaireAnalysis(data_fname)
    d.read_data()
    # print (d.data)
    d.remove_rows_without_mail()
    d.show_age_distrib()
    d.fill_na_with_mean()
    # print (d.data)
    d.correlate_gender_age()

    
        
        
